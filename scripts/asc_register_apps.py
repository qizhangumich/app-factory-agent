#!/usr/bin/env python3
"""
App Factory v2 — App Store Connect App Registration (automated)
==================================================================
Programmatically creates app entries in App Store Connect. For each app
in config/ios_apps.yaml, walks the name_options list and registers the
first name that App Store accepts. Saves the final approved name back to
state/ios_app_names.json for downstream steps.

Why this exists:
  App Store names are globally unique across the entire Apple developer
  base. Common names like "Tip Calculator Deluxe" or "Pomodoro Focus
  Timer" are usually taken. Doing it through the web UI means clicking
  through 5+ failed attempts per app. The API + a prioritized name list
  collapses the whole thing to one command.

Prerequisites:
  1. config/asc_api_key.json:
       {
         "team_id":   "FNGC54MTDA",
         "key_id":    "ABCD1234EF",
         "issuer_id": "69a6de70-1234-...",
         "key_path":  "D:/personal/ai_projects/keys/AuthKey_ABCD1234EF.p8"
       }
  2. pip install pyjwt cryptography requests pyyaml

Usage:
    python scripts/asc_register_apps.py            # register all 5 apps
    python scripts/asc_register_apps.py --dry-run  # show what would happen
    python scripts/asc_register_apps.py --ws ws_001_tipcalcdeluxe
"""

import argparse, json, sys, time
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT  = Path(__file__).parent.parent.resolve()
CFG_FILE   = REPO_ROOT / "config" / "ios_apps.yaml"
KEY_FILE   = REPO_ROOT / "config" / "asc_api_key.json"
STATE_FILE = REPO_ROOT / "state"  / "ios_app_names.json"

ASC_BASE = "https://api.appstoreconnect.apple.com/v1"


# ── Auth ────────────────────────────────────────────────────────────────────

def make_jwt(creds):
    """Generate an ES256 JWT for App Store Connect API.
    Token is valid for 20 min (max allowed).
    """
    import jwt  # PyJWT
    private_key = Path(creds["key_path"]).read_text()
    now = datetime.now(tz=timezone.utc)
    payload = {
        "iss": creds["issuer_id"],
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=20)).timestamp()),
        "aud": "appstoreconnect-v1",
    }
    headers = {"kid": creds["key_id"], "typ": "JWT"}
    return jwt.encode(payload, private_key, algorithm="ES256", headers=headers)


# ── ASC API helpers ────────────────────────────────────────────────────────

def asc_get(token, path, params=None):
    import requests
    r = requests.get(f"{ASC_BASE}{path}",
                     headers={"Authorization": f"Bearer {token}"},
                     params=params, timeout=30)
    return r


def asc_post(token, path, body):
    import requests
    r = requests.post(f"{ASC_BASE}{path}",
                      headers={"Authorization": f"Bearer {token}",
                               "Content-Type": "application/json"},
                      json=body, timeout=30)
    return r


def find_bundle_id(token, bundle_id_str):
    """Return the ASC bundle-id resource id for a given identifier string,
    or None if not registered yet."""
    r = asc_get(token, "/bundleIds",
                params={"filter[identifier]": bundle_id_str, "limit": 200})
    if r.status_code != 200:
        return None
    for item in r.json().get("data", []):
        if item["attributes"]["identifier"] == bundle_id_str:
            return item["id"]
    return None


def find_app(token, bundle_id_str):
    """Return the app id + current name if the app already exists, else
    (None, None)."""
    r = asc_get(token, "/apps",
                params={"filter[bundleId]": bundle_id_str, "limit": 10})
    if r.status_code != 200:
        return None, None
    for item in r.json().get("data", []):
        # Note: filter[bundleId] is fuzzy on some ASC endpoints; verify.
        return item["id"], item["attributes"].get("name")
    return None, None


def create_app(token, name, bundle_id_resource_id, sku, primary_locale):
    """Try to create an App Store Connect app entry. Returns (status_code,
    detail) — 201 = created, 409 = name taken or other conflict."""
    body = {
        "data": {
            "type": "apps",
            "attributes": {
                "bundleId":       None,   # not used here — relationship below
                "name":           name,
                "primaryLocale":  primary_locale,
                "sku":            sku,
            },
            "relationships": {
                "bundleId": {
                    "data": {"type": "bundleIds", "id": bundle_id_resource_id}
                }
            }
        }
    }
    # 'bundleId' attribute is read-only on create; only the relationship matters.
    del body["data"]["attributes"]["bundleId"]

    r = asc_post(token, "/apps", body)
    if r.status_code == 201:
        return 201, r.json()["data"]["id"]

    # parse the error detail
    try:
        errs = r.json().get("errors", [])
        details = "; ".join(e.get("detail", str(e)) for e in errs)
    except Exception:
        details = r.text[:200]
    return r.status_code, details


# ── Per-app registration loop ──────────────────────────────────────────────

def register_one(token, app, dry_run=False):
    ws       = app["workspace"]
    bid      = app["bundle_id"]
    sku      = app["sku"]
    locale   = app["primary_locale"]
    options  = app["name_options"]

    print(f"\n=== {ws} ({bid}) ===")

    # idempotency: if already created, skip
    existing_id, existing_name = find_app(token, bid)
    if existing_id:
        print(f"  [skip] already exists: '{existing_name}'  ({existing_id})")
        return {"workspace": ws, "bundle_id": bid, "app_id": existing_id,
                "name": existing_name, "status": "already_exists"}

    # need the bundleIds resource id (registered separately via the
    # Identifiers UI or POST /bundleIds — assume it exists since the
    # human has to register App IDs at developer.apple.com first)
    bres = find_bundle_id(token, bid)
    if not bres:
        print(f"  [error] Bundle ID '{bid}' not yet registered at "
              "developer.apple.com -> Identifiers -> App IDs. "
              "Register it first (see docs/IOS_PIPELINE.md), then re-run.")
        return {"workspace": ws, "bundle_id": bid, "status": "missing_bundle_id"}

    for i, name in enumerate(options, 1):
        if dry_run:
            print(f"  [dry-run] would try #{i}: '{name}'")
            continue

        print(f"  trying #{i}: '{name}'", end="")
        code, detail = create_app(token, name, bres, sku, locale)

        if code == 201:
            print(f"  -> [OK] created (app id {detail})")
            return {"workspace": ws, "bundle_id": bid, "app_id": detail,
                    "name": name, "status": "created"}
        elif "name" in detail.lower() and ("unique" in detail.lower() or "taken" in detail.lower() or "already" in detail.lower()):
            print(f"  -> name taken")
            continue
        elif code == 409:
            print(f"  -> conflict ({detail[:100]})")
            continue
        else:
            print(f"  -> [error {code}] {detail[:200]}")
            return {"workspace": ws, "bundle_id": bid, "status": "error",
                    "error": detail}

    print(f"  [FAIL] none of {len(options)} name options worked")
    return {"workspace": ws, "bundle_id": bid, "status": "all_names_taken"}


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="show what would be tried without calling ASC")
    ap.add_argument("--ws", help="register only this workspace")
    args = ap.parse_args()

    try:
        import yaml
    except ImportError:
        print("Install:  pip install pyyaml pyjwt cryptography requests")
        sys.exit(1)

    if not KEY_FILE.exists():
        print(f"\n[ERROR] missing {KEY_FILE.relative_to(REPO_ROOT)}\n")
        print("Create this file with:")
        print('  { "team_id": "FNGC54MTDA",')
        print('    "key_id": "<ASC Key ID>",')
        print('    "issuer_id": "<ASC Issuer ID>",')
        print('    "key_path": "D:/personal/ai_projects/keys/AuthKey_XXXXXXXXXX.p8" }')
        sys.exit(1)

    cfg   = yaml.safe_load(CFG_FILE.read_text(encoding="utf-8"))
    creds = json.loads(KEY_FILE.read_text(encoding="utf-8"))
    apps  = cfg["apps"]
    if args.ws:
        apps = [a for a in apps if a["workspace"] == args.ws]

    if not args.dry_run:
        token = make_jwt(creds)
        print(f"Authenticated with team {creds['team_id']}")
    else:
        token = None

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state = json.loads(STATE_FILE.read_text(encoding="utf-8")) if STATE_FILE.exists() else {"apps": []}
    by_ws = {a["workspace"]: a for a in state.get("apps", [])}

    for app in apps:
        result = register_one(token, app, dry_run=args.dry_run)
        if result.get("status") in ("created", "already_exists"):
            by_ws[app["workspace"]] = result

    if not args.dry_run:
        state["apps"] = list(by_ws.values())
        state["last_run"] = datetime.now(timezone.utc).isoformat()
        STATE_FILE.write_text(json.dumps(state, indent=2))
        print(f"\nSaved state -> {STATE_FILE.relative_to(REPO_ROOT)}")

    # Summary
    print("\n" + "=" * 60)
    print(f"{'Workspace':30} {'Status':20} Display name")
    print("=" * 60)
    for app in apps:
        r = by_ws.get(app["workspace"], {"status": "skipped"})
        print(f"{app['workspace']:30} {r['status']:20} {r.get('name','-')}")


if __name__ == "__main__":
    main()
