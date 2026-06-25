#!/usr/bin/env python3
"""
App Factory v2 — App Store review status dashboard
====================================================
Prints a single-screen status for every app the factory ships, fetched
live from Apple via the App Store Connect API.

Per app it shows:
  - App Store Connect app id
  - Current App Store version + state (Waiting for Review, In Review,
    Pending Developer Release, Ready for Sale, Rejected, etc.)
  - Build version that's attached
  - Latest review submission state (if any)
  - A direct App Store Connect URL you can paste into your browser

Run:  python scripts/asc_status.py
Refresh:  re-run any time; Apple updates the state in near-real-time.
"""

import json, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
KEY_FILE  = REPO_ROOT / "config" / "asc_api_key.json"
CFG_FILE  = REPO_ROOT / "config" / "ios_app_metadata.yaml"

ASC_BASE  = "https://api.appstoreconnect.apple.com/v1"

# Friendly labels for Apple's state strings (most common ones)
STATE_LABEL = {
    "PREPARE_FOR_SUBMISSION":   "Prepare for Submission",
    "WAITING_FOR_REVIEW":       "Waiting for Review",
    "IN_REVIEW":                "In Review",
    "PENDING_CONTRACT":         "Pending Contract",
    "PENDING_APPLE_RELEASE":    "Pending Apple Release",
    "PENDING_DEVELOPER_RELEASE":"Pending Developer Release",
    "PROCESSING_FOR_APP_STORE": "Processing for App Store",
    "READY_FOR_SALE":           "Ready for Sale (LIVE)",
    "READY_FOR_DISTRIBUTION":   "Ready for Distribution",
    "REJECTED":                 "Rejected",
    "METADATA_REJECTED":        "Metadata Rejected",
    "DEVELOPER_REJECTED":       "Developer Rejected",
    "DEVELOPER_REMOVED_FROM_SALE":"Removed from Sale",
    "REMOVED_FROM_SALE":        "Removed from Sale",
    "INVALID_BINARY":           "Invalid Binary",
    "READY_FOR_REVIEW":         "Ready for Review",
}


def make_jwt(creds):
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


def asc_get(token, path):
    import requests
    return requests.get(f"{ASC_BASE}{path}",
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=30)


def get_app_status(token, app_id):
    """Return a dict summarizing the app's review status."""
    out = {"app_id": app_id, "name": None, "version": None,
           "version_state": None, "build_version": None,
           "submission_state": None}

    # App basics
    r = asc_get(token, f"/apps/{app_id}")
    if r.status_code == 200:
        out["name"] = r.json().get("data", {}).get("attributes", {}).get("name")

    # Latest App Store version (Apple's sort param on this endpoint is
    # restricted; just get a small list and pick by createdDate)
    r = asc_get(token, f"/apps/{app_id}/appStoreVersions?limit=10")
    if r.status_code == 200 and r.json().get("data"):
        versions = sorted(
            r.json()["data"],
            key=lambda v: v["attributes"].get("createdDate") or "",
            reverse=True,
        )
        v = versions[0]
        out["version"] = v["attributes"].get("versionString")
        state = v["attributes"].get("appStoreState") or v["attributes"].get("appVersionState") or ""
        out["version_state"] = STATE_LABEL.get(state, state)
        # Build attached?
        version_id = v["id"]
        r2 = asc_get(token, f"/appStoreVersions/{version_id}/build")
        if r2.status_code == 200 and r2.json().get("data"):
            out["build_version"] = r2.json()["data"]["attributes"].get("version")

    # Latest review submission
    r = asc_get(token, f"/reviewSubmissions?filter[app]={app_id}&limit=10")
    if r.status_code == 200:
        for s in r.json().get("data", []):
            state = s["attributes"].get("state", "")
            # Skip empty/canceled drafts; surface the most informative one
            if state in ("READY_FOR_REVIEW", "IN_PROGRESS"):
                # check if items attached; if not, skip (it's an orphan)
                items_r = asc_get(token, f"/reviewSubmissions/{s['id']}/items")
                if items_r.status_code == 200 and not items_r.json().get("data"):
                    continue
            out["submission_state"] = STATE_LABEL.get(state, state)
            break

    return out


def main():
    try:
        import yaml, requests, jwt
    except ImportError:
        print("Install:  pip install pyyaml pyjwt cryptography requests")
        sys.exit(1)

    if not KEY_FILE.exists():
        print(f"missing {KEY_FILE}")
        sys.exit(1)

    cfg   = yaml.safe_load(CFG_FILE.read_text(encoding="utf-8"))
    creds = json.loads(KEY_FILE.read_text())
    token = make_jwt(creds)

    print(f"\nApp Factory iOS — Apple Review Status  (team {creds['team_id']})")
    print(f"Fetched {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # Header
    print(f"{'Workspace':28} {'App':28} {'Version state':28} {'Submission state':22} Build")
    print("-" * 130)

    # Cache: workspace -> app_id, looked up via bundle_id from ASC API.
    def lookup_app_id(bundle_id):
        r = asc_get(token, f"/apps?filter[bundleId]={bundle_id}&limit=10")
        if r.status_code != 200:
            return None
        for item in r.json().get("data", []):
            if item["attributes"].get("bundleId") == bundle_id:
                return item["id"]
        data = r.json().get("data", [])
        return data[0]["id"] if data else None

    for app in cfg["apps"]:
        ws = app["workspace"]
        ws_json = REPO_ROOT / "workspaces" / ws / "workspace.json"
        bundle = json.loads(ws_json.read_text())["bundle_id_ios"]
        app_id = lookup_app_id(bundle)
        if not app_id:
            print(f"{ws:28} (no ASC app for {bundle})")
            continue
        s = get_app_status(token, app_id)
        print(f"{ws:28} {(s['name'] or '?')[:28]:28} {(s['version_state'] or '-'):28} "
              f"{(s['submission_state'] or '-'):22} {s.get('build_version') or '-'}")
        print(f"{'':28} https://appstoreconnect.apple.com/apps/{app_id}/distribution/ios/version/inflight")

    print()
    print("Direct App Store Connect link template:")
    print("  https://appstoreconnect.apple.com/apps/<APP_ID>/distribution/ios/version/inflight")
    print()


if __name__ == "__main__":
    main()
