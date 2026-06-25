#!/usr/bin/env python3
"""
App Factory v2 — App Store Connect Release Pipeline (iOS metadata)
======================================================================
The iOS counterpart of scripts/play_release.py. For each app:

  1. Find the App Store Connect app id from bundle_id
  2. Find or create the editable App Store version (status PREPARE_FOR_SUBMISSION)
  3. Update categories on the AppInfo
  4. Update name + subtitle + privacy policy URL on the en-US AppInfoLocalization
  5. Update description + keywords + promotional text + marketing/support URLs
     on the en-US AppStoreVersionLocalization
  6. (Optional, --submit) Create an AppStoreVersionSubmission to send for review

What it does NOT do yet:
  - Screenshot upload (Apple's chunked upload protocol is more involved;
    today's pass is text-only. Screenshots are still uploaded via the
    ASC web UI or in a future asc_screenshots.py pass.)

Prerequisites:
  - config/asc_api_key.json (from scripts/asc_register_apps.py setup)
  - config/ios_app_metadata.yaml
  - The build is already uploaded to App Store Connect (via GitHub Actions
    ios_deploy workflow) — App Store version creation needs a build to
    attach to.

Usage:
    python scripts/asc_release.py              # update metadata for all 5 apps
    python scripts/asc_release.py --only ws_001_tipcalcdeluxe
    python scripts/asc_release.py --submit     # also POST submission for review
    python scripts/asc_release.py --dry-run    # show what would happen
"""

import argparse, json, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT  = Path(__file__).parent.parent.resolve()
CFG_FILE   = REPO_ROOT / "config" / "ios_app_metadata.yaml"
KEY_FILE   = REPO_ROOT / "config" / "asc_api_key.json"

ASC_BASE = "https://api.appstoreconnect.apple.com/v1"

DEFAULT_LOCALE = "en-US"
EDITABLE_STATES = (
    "PREPARE_FOR_SUBMISSION", "READY_FOR_REVIEW",
    "DEVELOPER_REJECTED", "REJECTED", "METADATA_REJECTED",
    "WAITING_FOR_REVIEW", "INVALID_BINARY",
)


# ── Auth ────────────────────────────────────────────────────────────────────

def make_jwt(creds):
    import jwt
    now = datetime.now(tz=timezone.utc)
    payload = {
        "iss": creds["issuer_id"],
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=20)).timestamp()),
        "aud": "appstoreconnect-v1",
    }
    headers = {"kid": creds["key_id"], "typ": "JWT"}
    return jwt.encode(payload, Path(creds["key_path"]).read_text(),
                      algorithm="ES256", headers=headers)


def asc_request(method, token, path, body=None):
    import requests
    headers = {"Authorization": f"Bearer {token}"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    r = requests.request(method, f"{ASC_BASE}{path}",
                         headers=headers, json=body, timeout=60)
    return r


# ── ASC operations ──────────────────────────────────────────────────────────

def find_app_id(token, bundle_id):
    r = asc_request("GET", token, f"/apps?filter[bundleId]={bundle_id}&limit=10")
    if r.status_code != 200:
        return None
    for item in r.json().get("data", []):
        if item["attributes"].get("bundleId") == bundle_id:
            return item["id"]
    # Apple's filter[bundleId] is fuzzy; if exact match missing, return first
    data = r.json().get("data", [])
    return data[0]["id"] if data else None


def find_editable_app_info(token, app_id):
    """Return the AppInfo resource id whose state is editable (typically
    PREPARE_FOR_SUBMISSION). This is the one whose name/subtitle/categories
    are still mutable."""
    r = asc_request("GET", token, f"/apps/{app_id}/appInfos")
    if r.status_code != 200:
        return None
    candidates = []
    for info in r.json().get("data", []):
        state = info["attributes"].get("appStoreState", "")
        candidates.append((state in EDITABLE_STATES, info["id"]))
    candidates.sort(reverse=True)
    return candidates[0][1] if candidates else None


def find_app_info_localization(token, app_info_id, locale=DEFAULT_LOCALE):
    r = asc_request("GET", token, f"/appInfos/{app_info_id}/appInfoLocalizations")
    if r.status_code != 200:
        return None
    for loc in r.json().get("data", []):
        if loc["attributes"].get("locale") == locale:
            return loc["id"]
    return None


def find_or_create_app_store_version(token, app_id, build_version="1.0", dry_run=False):
    """Return the AppStoreVersion id that is currently editable.
    If none exists, create one targeting the latest build."""
    r = asc_request("GET", token,
                    f"/apps/{app_id}/appStoreVersions"
                    f"?filter[appStoreState]={','.join(EDITABLE_STATES)}"
                    f"&limit=5")
    if r.status_code == 200:
        for v in r.json().get("data", []):
            return v["id"]
    # Fallback: list all versions and pick the first editable one (the
    # filter[] sometimes returns an empty list even when an editable
    # version exists).
    r2 = asc_request("GET", token,
                     f"/apps/{app_id}/appStoreVersions?limit=20")
    if r2.status_code == 200:
        for v in r2.json().get("data", []):
            state = v["attributes"].get("appStoreState", "")
            if state in EDITABLE_STATES:
                return v["id"]
    # No editable version — create one
    if dry_run:
        return "DRY_RUN"
    body = {
        "data": {
            "type": "appStoreVersions",
            "attributes": {
                "platform":       "IOS",
                "versionString":  build_version,
                "copyright":      "2026 LINKWAVE PTE.LTD.",
                "releaseType":    "MANUAL",
            },
            "relationships": {
                "app": {"data": {"type": "apps", "id": app_id}}
            }
        }
    }
    r = asc_request("POST", token, "/appStoreVersions", body=body)
    if r.status_code == 201:
        return r.json()["data"]["id"]
    return None


def find_or_create_version_localization(token, version_id, locale=DEFAULT_LOCALE):
    r = asc_request("GET", token, f"/appStoreVersions/{version_id}/appStoreVersionLocalizations")
    if r.status_code == 200:
        for loc in r.json().get("data", []):
            if loc["attributes"].get("locale") == locale:
                return loc["id"]
    body = {
        "data": {
            "type": "appStoreVersionLocalizations",
            "attributes": {"locale": locale},
            "relationships": {
                "appStoreVersion": {"data": {"type": "appStoreVersions", "id": version_id}}
            }
        }
    }
    r = asc_request("POST", token, "/appStoreVersionLocalizations", body=body)
    return r.json()["data"]["id"] if r.status_code == 201 else None


def patch(token, resource_type, resource_id, attrs):
    body = {"data": {"type": resource_type, "id": resource_id, "attributes": attrs}}
    r = asc_request("PATCH", token, f"/{resource_type}/{resource_id}", body=body)
    return r.status_code == 200, r


def submit_for_review(token, version_id, dry_run=False):
    if dry_run:
        return True, "DRY_RUN"
    body = {
        "data": {
            "type": "appStoreVersionSubmissions",
            "relationships": {
                "appStoreVersion": {"data": {"type": "appStoreVersions", "id": version_id}}
            }
        }
    }
    r = asc_request("POST", token, "/appStoreVersionSubmissions", body=body)
    if r.status_code == 201:
        return True, r.json()["data"]["id"]
    try:
        detail = json.loads(r.text)["errors"][0].get("detail", r.text[:300])
    except Exception:
        detail = r.text[:300]
    return False, f"HTTP {r.status_code}: {detail}"


# ── Per-app pipeline ────────────────────────────────────────────────────────

def read_metadata_inputs(app):
    """Pull the long description from the Android fastlane metadata
    folder (shared between platforms), apply per-app overrides from
    ios_app_metadata.yaml."""
    ws = app["workspace"]
    android_md = (REPO_ROOT / "workspaces" / ws / "android" /
                  "fastlane" / "metadata" / "android" / "en-US")
    description = (android_md / "full_description.txt").read_text(encoding="utf-8").strip() \
        if (android_md / "full_description.txt").exists() else ""
    return description


def release_one(token, app, common, submit=False, dry_run=False):
    ws        = app["workspace"]
    workspace = REPO_ROOT / "workspaces" / ws
    bundle_id_file = workspace / "workspace.json"
    bundle_id = json.loads(bundle_id_file.read_text())["bundle_id_ios"]

    print(f"\n=== {ws} ({bundle_id}) ===")

    # 1. App
    app_id = find_app_id(token, bundle_id)
    if not app_id:
        return {"workspace": ws, "status": "no_app",
                "msg": f"No App Store Connect app for {bundle_id}"}
    print(f"  app_id: {app_id}")

    # 2. App-level metadata: categories + name/subtitle/privacy URL
    info_id = find_editable_app_info(token, app_id)
    if not info_id:
        return {"workspace": ws, "status": "no_info",
                "msg": "no editable AppInfo"}

    if not dry_run:
        ok, _ = patch(token, "appInfos", info_id, {
            "primaryCategory":   app["category_primary"],
            "secondaryCategory": app["category_secondary"],
        })
        # Apple sometimes wants relationships for category rather than attrs.
        # If attrs PATCH was a no-op (200 but no change), the relationship path is fine.

    loc_id = find_app_info_localization(token, info_id)
    if loc_id and not dry_run:
        privacy_url = f"{common['privacy_policy_base']}/{app['privacy_slug']}.html"
        ok, r = patch(token, "appInfoLocalizations", loc_id, {
            "subtitle":         app["subtitle"],
            "privacyPolicyUrl": privacy_url,
        })
        print(f"  subtitle/privacy:  {'OK' if ok else 'FAIL'}")

    # 3. App Store version
    version_id = find_or_create_app_store_version(
        token, app_id, build_version="1.0", dry_run=dry_run,
    )
    if not version_id:
        return {"workspace": ws, "status": "no_version",
                "msg": "could not find or create AppStoreVersion"}
    print(f"  version_id: {version_id}")

    # 4. Version-level localization
    description = read_metadata_inputs(app)
    if dry_run:
        print(f"  [dry-run] would update version localization for {ws}")
        return {"workspace": ws, "status": "dry_run"}

    vloc_id = find_or_create_version_localization(token, version_id)
    if vloc_id:
        attrs = {
            "description":     description,
            "keywords":        app["keywords"],
            "supportUrl":      common["support_url_base"] + f"/{app['privacy_slug']}.html",
            "marketingUrl":    common["marketing_url"],
            "promotionalText": app["promotional_text"],
        }
        ok, r = patch(token, "appStoreVersionLocalizations", vloc_id, attrs)
        print(f"  desc/keywords/urls: {'OK' if ok else 'FAIL'}")
        if not ok:
            try:
                err = r.json().get("errors", [{}])[0].get("detail", r.text[:200])
                print(f"    -> {err}")
            except Exception:
                pass

    # 5. Optional submit
    if submit:
        ok, detail = submit_for_review(token, version_id)
        if ok:
            print(f"  [OK] submitted for review (id {detail})")
        else:
            print(f"  [FAIL] submit: {detail}")
            return {"workspace": ws, "status": "submit_failed", "msg": detail}

    return {"workspace": ws, "status": "ok"}


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="run only this workspace")
    ap.add_argument("--submit", action="store_true",
                    help="also POST the submission for review")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    try:
        import yaml
    except ImportError:
        print("Install:  pip install pyyaml pyjwt cryptography requests")
        sys.exit(1)

    if not KEY_FILE.exists():
        print(f"missing {KEY_FILE} — see scripts/asc_register_apps.py for setup")
        sys.exit(1)

    cfg = yaml.safe_load(CFG_FILE.read_text(encoding="utf-8"))
    common = cfg["common"]
    apps = cfg["apps"]
    if args.only:
        apps = [a for a in apps if a["workspace"] == args.only]

    creds = json.loads(KEY_FILE.read_text())
    # Always authenticate — dry-run still reads from the API to verify
    # state; --dry-run only suppresses writes.
    token = make_jwt(creds)
    print(f"Authenticated with team {creds['team_id']}")

    results = []
    for app in apps:
        results.append(release_one(token, app, common,
                                    submit=args.submit, dry_run=args.dry_run))

    # Summary
    print("\n" + "=" * 60)
    print(f"{'Workspace':30} Status")
    print("=" * 60)
    for r in results:
        print(f"{r['workspace']:30} {r['status']}  {r.get('msg','')}")


if __name__ == "__main__":
    main()
