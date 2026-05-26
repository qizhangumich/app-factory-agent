#!/usr/bin/env python3
"""
App Factory v2 — Google Play Delivery Script
=============================================
Uploads signed AABs for all Phase-1 Android apps to the Play Store
internal track using the Google Play Developer API (no fastlane needed).

Usage:
    python scripts/play_deliver.py

Prerequisites:
  1. pip install google-api-python-client google-auth
  2. Save service account JSON to: config/play_service_account.json
  3. Grant the service account "Release manager" in Play Console
  4. Create each app listing in Play Console (package name must exist)
  5. Run this script

Environment overrides:
  PLAY_JSON_KEY_FILE  — override the JSON key path
  PLAY_TRACK          — override the release track (default: internal)
"""

import os
import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()

APPS = [
    {
        "name":      "Tip Calculator Deluxe",
        "workspace": "ws_001_tipcalcdeluxe",
        "package":   "com.appfactory.tipcalcdeluxe",
    },
    {
        "name":      "Unit Converter Pro",
        "workspace": "ws_002_unitconverterpro",
        "package":   "com.appfactory.unitconverterpro",
    },
    {
        "name":      "QR & Barcode Scanner+",
        "workspace": "ws_004_qrbarcodescanner",
        "package":   "com.appfactory.qrbarcodescanner",
    },
    {
        "name":      "Pomodoro Focus Timer",
        "workspace": "ws_005_pomodorofocus",
        "package":   "com.appfactory.pomodorofocus",
    },
]

JSON_KEY = os.environ.get(
    "PLAY_JSON_KEY_FILE",
    str(REPO_ROOT / "config" / "play_service_account.json")
)
TRACK = os.environ.get("PLAY_TRACK", "internal")


def banner(msg: str) -> None:
    print(f"\n{'='*60}\n  {msg}\n{'='*60}")


def aab_path(ws: str) -> Path:
    return (REPO_ROOT / "workspaces" / ws / "android" /
            "app" / "build" / "outputs" / "bundle" / "release" / "app-release.aab")


def build_service(json_key_path: str):
    """Build authenticated Google Play API service.
    Prefers OAuth2 user token (config/play_oauth_token.json) over service
    account key — user token always has full account owner permissions.
    """
    from googleapiclient.discovery import build

    oauth_token = REPO_ROOT / "config" / "play_oauth_token.json"
    if oauth_token.exists():
        import json
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        data  = json.loads(oauth_token.read_text())
        creds = Credentials(
            token=data["token"],
            refresh_token=data["refresh_token"],
            token_uri=data["token_uri"],
            client_id=data["client_id"],
            client_secret=data["client_secret"],
            scopes=data["scopes"],
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Persist refreshed token
            data["token"] = creds.token
            oauth_token.write_text(json.dumps(data, indent=2))
        print("Auth method: OAuth2 user credentials")
        return build("androidpublisher", "v3", credentials=creds, cache_discovery=False)

    # Fallback: service account key
    from google.oauth2 import service_account
    creds = service_account.Credentials.from_service_account_file(
        json_key_path,
        scopes=["https://www.googleapis.com/auth/androidpublisher"]
    )
    print("Auth method: service account")
    return build("androidpublisher", "v3", credentials=creds, cache_discovery=False)


def upload_app(service, app: dict) -> bool:
    """Upload AAB to Play internal track. Returns True on success."""
    from googleapiclient.http import MediaFileUpload

    name    = app["name"]
    pkg     = app["package"]
    aab     = aab_path(app["workspace"])

    banner(f"Uploading: {name}")
    print(f"  Package : {pkg}")
    print(f"  AAB     : {aab}")
    print(f"  Track   : {TRACK}")

    if not aab.exists():
        print(f"\n  [SKIP] AAB not found: {aab}")
        return False

    try:
        edits = service.edits()

        # 1. Open a new edit
        edit = edits.insert(packageName=pkg, body={}).execute()
        edit_id = edit["id"]
        print(f"\n  Edit opened: {edit_id}")

        # 2. Upload the AAB
        print(f"  Uploading AAB ({aab.stat().st_size // 1024 // 1024} MB)...")
        media = MediaFileUpload(str(aab), mimetype="application/octet-stream",
                                resumable=True, chunksize=10 * 1024 * 1024)
        bundle = edits.bundles().upload(
            packageName=pkg,
            editId=edit_id,
            media_body=media
        ).execute()
        version_code = bundle["versionCode"]
        print(f"  Bundle uploaded — versionCode: {version_code}")

        # 3. Assign to track
        track_body = {
            "track": TRACK,
            "releases": [{
                "status": "draft",
                "versionCodes": [str(version_code)],
                "releaseNotes": [{"language": "en-US", "text": "Initial release"}]
            }]
        }
        edits.tracks().update(
            packageName=pkg,
            editId=edit_id,
            track=TRACK,
            body=track_body
        ).execute()
        print(f"  Assigned to '{TRACK}' track as draft")

        # 4. Commit the edit
        edits.commit(packageName=pkg, editId=edit_id).execute()
        print(f"\n  [OK] {name} uploaded successfully")
        return True

    except Exception as e:
        err = str(e)
        # Extract useful message from Google API error
        try:
            detail = json.loads(e.content.decode())["error"]["message"]  # type: ignore
            err = detail
        except Exception:
            pass
        print(f"\n  [FAIL] {name}: {err}")
        return False


def main() -> None:
    banner("App Factory v2 — Google Play Delivery")
    print(f"Repo  : {REPO_ROOT}")
    print(f"Key   : {JSON_KEY}")
    print(f"Track : {TRACK}")

    # Check prerequisites
    if not Path(JSON_KEY).exists():
        print(f"\n[ERROR] Service account JSON not found:\n  {JSON_KEY}")
        sys.exit(1)

    try:
        service = build_service(JSON_KEY)
    except Exception as e:
        print(f"\n[ERROR] Failed to authenticate: {e}")
        sys.exit(1)

    print("\nAuthenticated with Google Play API [OK]")

    results = {}
    for app in APPS:
        ok = upload_app(service, app)
        results[app["name"]] = "[OK] uploaded" if ok else "[FAIL] failed/skipped"

    banner("Delivery Summary")
    for name, status in results.items():
        print(f"  {status}  {name}")

    print("\nNext step: Play Console → Internal testing → promote to Production")
    print("           when ready (human gate).\n")


if __name__ == "__main__":
    main()
