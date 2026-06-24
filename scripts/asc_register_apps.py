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


def register_bundle_id(token, bundle_id_str, name):
    """Create a new App ID (bundle ID) at the Apple Developer level.
    Equivalent to clicking through developer.apple.com -> Identifiers.
    Returns (resource_id, error_detail or None).

    Apple's developer-portal name has stricter rules than the App Store
    display name: no '+', '&', etc. Caller should sanitize.
    """
    # sanitize for developer-portal restrictions
    import re
    safe_name = re.sub(r"[^A-Za-z0-9 ]", "", name).strip() or "App"

    body = {
        "data": {
            "type": "bundleIds",
            "attributes": {
                "identifier": bundle_id_str,
                "name":       safe_name,
                "platform":   "IOS",   # iOS App ID
            }
        }
    }
    r = asc_post(token, "/bundleIds", body)
    if r.status_code == 201:
        return r.json()["data"]["id"], None
    try:
        errs = r.json().get("errors", [])
        detail = "; ".join(e.get("detail", str(e)) for e in errs)
    except Exception:
        detail = r.text[:200]
    return None, f"HTTP {r.status_code}: {detail}"


def asc_patch(token, path, body):
    import requests
    r = requests.patch(f"{ASC_BASE}{path}",
                       headers={"Authorization": f"Bearer {token}",
                                "Content-Type": "application/json"},
                       json=body, timeout=30)
    return r


def get_editable_localization_id(token, app_id, locale="en-US"):
    """Find the AppInfoLocalization for the editable AppInfo (state
    PREPARE_FOR_SUBMISSION or READY_FOR_REVIEW). Returns (loc_id, current_name)."""
    r = asc_get(token, f"/apps/{app_id}/appInfos")
    if r.status_code != 200:
        return None, None
    # Prefer editable state
    editable_states = ("PREPARE_FOR_SUBMISSION", "READY_FOR_REVIEW",
                        "DEVELOPER_REJECTED", "REJECTED", "METADATA_REJECTED",
                        "WAITING_FOR_REVIEW", "INVALID_BINARY")
    candidates = []
    for info in r.json().get("data", []):
        state = info["attributes"].get("appStoreState", "")
        candidates.append((state in editable_states, info["id"]))
    candidates.sort(reverse=True)  # editable first
    for _, info_id in candidates:
        r2 = asc_get(token, f"/appInfos/{info_id}/appInfoLocalizations")
        if r2.status_code != 200:
            continue
        for loc in r2.json().get("data", []):
            if loc["attributes"].get("locale") == locale:
                return loc["id"], loc["attributes"].get("name")
    return None, None


def rename_app(token, app_id, new_name, locale="en-US"):
    """Rename an app's en-US display name. Apple stores this on
    AppInfoLocalization, not on the App itself. Returns (success_bool, error_or_None)."""
    loc_id, _ = get_editable_localization_id(token, app_id, locale)
    if not loc_id:
        return False, "no editable AppInfoLocalization found for this app"

    body = {
        "data": {
            "type": "appInfoLocalizations",
            "id":   loc_id,
            "attributes": {"name": new_name},
        }
    }
    r = asc_patch(token, f"/appInfoLocalizations/{loc_id}", body)
    if r.status_code == 200:
        return True, None
    try:
        errs = r.json().get("errors", [])
        detail = "; ".join(e.get("detail", str(e)) for e in errs)
    except Exception:
        detail = r.text[:200]
    return False, f"HTTP {r.status_code}: {detail}"


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

    # idempotency: if already created, try to upgrade the name
    existing_id, existing_name = find_app(token, bid)
    if existing_id:
        # If the current name is already one of our top choices, leave it
        if existing_name in options:
            idx = options.index(existing_name)
            if idx == 0:
                print(f"  [skip] already named first-choice '{existing_name}'")
            else:
                # try to rename to a higher-ranked option
                for better in options[:idx]:
                    if dry_run:
                        print(f"  [dry-run] would try renaming to '{better}'")
                        continue
                    print(f"  trying rename to '{better}'...", end="")
                    ok, err = rename_app(token, existing_id, better)
                    if ok:
                        print(f"  -> [OK] renamed")
                        existing_name = better
                        break
                    else:
                        print(f"  -> taken")
            return {"workspace": ws, "bundle_id": bid, "app_id": existing_id,
                    "name": existing_name, "status": "already_exists"}
        # otherwise (ugly name like "...1"), try every option to upgrade
        print(f"  current name '{existing_name}' is off-list — trying to upgrade")
        for better in options:
            if dry_run:
                print(f"  [dry-run] would try renaming to '{better}'")
                continue
            print(f"  trying rename to '{better}'...", end="")
            ok, err = rename_app(token, existing_id, better)
            if ok:
                print(f"  -> [OK] renamed")
                return {"workspace": ws, "bundle_id": bid, "app_id": existing_id,
                        "name": better, "status": "renamed"}
            else:
                print(f"  -> taken")
        # no rename worked — keep the original name
        return {"workspace": ws, "bundle_id": bid, "app_id": existing_id,
                "name": existing_name, "status": "already_exists_no_rename"}

    # Find or auto-create the bundleIds resource. Apple's API allows
    # programmatic creation of App IDs, so we don't need to click
    # through developer.apple.com -> Identifiers manually.
    bres = find_bundle_id(token, bid)
    if not bres:
        # auto-register the App ID. Name = first option (used as
        # internal description in the Apple Developer portal — users
        # never see this).
        print(f"  registering App ID '{bid}'...", end="")
        bres, err = register_bundle_id(token, bid, options[0])
        if not bres:
            print(f"  -> [error] {err}")
            return {"workspace": ws, "bundle_id": bid, "status": "bundle_id_error",
                    "error": err}
        print(f"  -> [OK] ({bres})")

    # NOTE: Apple removed the POST /apps endpoint around 2020 to prevent
    # spam app creation. The app entry MUST be created via App Store
    # Connect web UI by a human. After it's created, re-run this script
    # to auto-rename to the best available name from the options list.
    print(f"  [action needed] Bundle ID is registered. Now go to:")
    print(f"    https://appstoreconnect.apple.com/apps")
    print(f"  Click '+' -> New App -> select platform 'iOS' ->")
    print(f"  pick Bundle ID '{bid}' from the dropdown ->")
    print(f"  use ANY placeholder name (e.g. 'Untitled') + SKU '{sku}'.")
    print(f"  Re-run this script and it will auto-rename to a better name.")
    return {"workspace": ws, "bundle_id": bid, "bundle_id_resource": bres,
            "status": "needs_ui_creation"}


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
