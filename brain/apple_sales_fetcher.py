"""Apple App Store sales fetcher — Layer 1 input.

Pulls one day's sales data from the App Store Connect Sales Reports API
and returns it as a normalized list of revenue events that
revenue_tracker.record_revenue() consumes.

Apple's Sales Report endpoint:
    GET /v1/salesReports
returns a gzipped TSV. Columns of interest:
    SKU, Title, Apple Identifier, Units, Developer Proceeds,
    Country Code, Currency of Proceeds, Begin Date

Vendor number is required and must be supplied via config/asc_api_key.json
(extra `vendor_number` field). Find it in App Store Connect web UI:
  Payments and Financial Reports → top of page (8-digit number).

Run:
    python -m brain.apple_sales_fetcher --date 2026-06-25
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
KEY_FILE  = REPO_ROOT / "config" / "asc_api_key.json"

ASC_BASE = "https://api.appstoreconnect.apple.com/v1"


def _make_token(creds: dict) -> str:
    import jwt
    now = datetime.now(tz=timezone.utc)
    return jwt.encode({
        "iss": creds["issuer_id"],
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=20)).timestamp()),
        "aud": "appstoreconnect-v1",
    }, Path(creds["key_path"]).read_text(),
        algorithm="ES256",
        headers={"kid": creds["key_id"], "typ": "JWT"})


def _load_creds() -> dict:
    if not KEY_FILE.exists():
        raise SystemExit(f"missing {KEY_FILE}")
    creds = json.loads(KEY_FILE.read_text())
    if not creds.get("vendor_number"):
        raise SystemExit(
            f"\nMissing 'vendor_number' in {KEY_FILE}.\n\n"
            "Find it at: https://appstoreconnect.apple.com/itc/payments_and_financial_reports\n"
            "  Top of the page — an 8-digit number under the LINKWAVE PTE.LTD. team.\n\n"
            "Then add it to the JSON:\n"
            '  {"team_id": "...", "key_id": "...", "issuer_id": "...",\n'
            '   "key_path": "...", "vendor_number": "12345678"}'
        )
    return creds


def fetch_sales(report_date: str | None = None) -> list[dict]:
    """Pull one day's sales for our vendor. Returns a list of dicts:
        {date, apple_identifier, sku, title, units, proceeds_usd,
         country, currency}
    Empty list when there are no sales (also returned when the report
    isn't available yet — Apple publishes the prior day around mid-day
    Pacific).
    """
    import requests

    creds = _load_creds()
    if not report_date:
        # Apple publishes the prior day's report around 8am PT.
        # Default to "yesterday in UTC" which is safe for a daily cron.
        report_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

    token = _make_token(creds)
    params = {
        "filter[reportType]":    "SALES",
        "filter[reportSubType]": "SUMMARY",
        "filter[frequency]":     "DAILY",
        "filter[reportDate]":    report_date,
        "filter[vendorNumber]":  creds["vendor_number"],
        "filter[version]":       "1_1",
    }
    r = requests.get(f"{ASC_BASE}/salesReports",
                     headers={"Authorization": f"Bearer {token}",
                              "Accept": "application/a-gzip"},
                     params=params, timeout=60)

    if r.status_code == 404:
        # Apple returns 404 when no report exists for that date yet
        # (apps may not have published any sales). That's normal — we
        # just have nothing to record.
        return []
    if r.status_code != 200:
        raise SystemExit(f"Sales API HTTP {r.status_code}: {r.text[:500]}")

    # Body is gzipped TSV
    tsv_bytes = gzip.decompress(r.content)
    reader = csv.DictReader(io.StringIO(tsv_bytes.decode("utf-8")), delimiter="\t")

    events = []
    for row in reader:
        try:
            units    = int(row.get("Units", "0") or "0")
            proceeds = float(row.get("Developer Proceeds", "0") or "0")
        except ValueError:
            continue
        if units == 0 and proceeds == 0:
            continue
        events.append({
            "date":             row.get("Begin Date") or report_date,
            "apple_identifier": row.get("Apple Identifier", "").strip(),
            "sku":              row.get("SKU", "").strip(),
            "title":            row.get("Title", "").strip(),
            "units":            units,
            "proceeds_usd":     proceeds,        # NB: in Currency of Proceeds, often USD
            "country":          row.get("Country Code", "").strip(),
            "currency":         row.get("Currency of Proceeds", "").strip(),
        })
    return events


def map_to_workspace(events: list[dict]) -> list[dict]:
    """Attach our workspace_id + account_id to each event, using
    state/ios_app_names.json (apple_identifier -> workspace folder)
    and state/apps.json (workspace_id -> ios_account)."""
    name_file = REPO_ROOT / "state" / "ios_app_names.json"
    apps_file = REPO_ROOT / "state" / "apps.json"

    apple_id_to_ws = {}
    if name_file.exists():
        for a in json.loads(name_file.read_text()).get("apps", []):
            ws = a.get("workspace", "")
            # workspace strings look like "ws_001_tipcalcdeluxe"
            ws_id = ws.split("_", 2)[0] + "_" + ws.split("_", 2)[1] if "_" in ws else ws
            apple_id_to_ws[a.get("app_id")] = ws_id

    ws_to_account = {}
    if apps_file.exists():
        for app in json.loads(apps_file.read_text()).get("apps", []):
            ws_to_account[app["workspace_id"]] = app.get("ios_account")

    enriched = []
    for ev in events:
        ws_id      = apple_id_to_ws.get(ev["apple_identifier"])
        account_id = ws_to_account.get(ws_id)
        enriched.append({**ev,
                         "workspace_id": ws_id,
                         "account_id":   account_id})
    return enriched


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-MM-DD; default: yesterday UTC")
    args = ap.parse_args()

    events = fetch_sales(args.date)
    enriched = map_to_workspace(events)

    print(f"Fetched {len(enriched)} sales row(s) for {args.date or 'yesterday'}.")
    for ev in enriched:
        print(f"  ws={ev.get('workspace_id') or '?':10}  "
              f"units={ev['units']:>4}  "
              f"proceeds={ev['proceeds_usd']:>7.2f} {ev['currency']}  "
              f"country={ev['country']}  "
              f"title={ev['title']}")
    if not enriched:
        print("  (no sales yet — normal if apps are still in review)")


if __name__ == "__main__":
    main()
