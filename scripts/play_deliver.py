#!/usr/bin/env python3
"""
App Factory v2 — Google Play Delivery Script
=============================================
Uploads signed AABs for all Phase-1 Android apps to the Play Store
internal track via fastlane supply.

Usage:
    python scripts/play_deliver.py

Prerequisites (one-time setup — see docs/ANDROID_SHIPPING.md):
  1. Create a Google Play service account JSON key and save it to:
         config/play_service_account.json
  2. Create each app in Play Console (package name must match below).
  3. Run this script — it uploads each AAB to the internal track as a draft.
  4. In Play Console, promote the draft release to production (human gate).

Environment overrides:
  PLAY_JSON_KEY_FILE  — override the JSON key path
  PLAY_TRACK          — override the release track (default: internal)
"""

import os
import subprocess
import sys
from pathlib import Path

# ── Configuration ───────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent.resolve()

APPS = [
    {
        "name":       "Tip Calculator Deluxe",
        "workspace":  "ws_001_tipcalcdeluxe",
        "package":    "com.appfactory.tipcalcdeluxe",
    },
    {
        "name":       "Unit Converter Pro",
        "workspace":  "ws_002_unitconverterpro",
        "package":    "com.appfactory.unitconverterpro",
    },
    {
        "name":       "QR & Barcode Scanner+",
        "workspace":  "ws_004_qrbarcodescanner",
        "package":    "com.appfactory.qrbarcodescanner",
    },
    {
        "name":       "Pomodoro Focus Timer",
        "workspace":  "ws_005_pomodorofocus",
        "package":    "com.appfactory.pomodorofocus",
    },
]

JSON_KEY = os.environ.get(
    "PLAY_JSON_KEY_FILE",
    str(REPO_ROOT / "config" / "play_service_account.json")
)
TRACK = os.environ.get("PLAY_TRACK", "internal")

# ── Helpers ─────────────────────────────────────────────────────────────────

def banner(msg: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print('='*60)

def check_prerequisites() -> None:
    """Abort early if the JSON key is missing."""
    if not Path(JSON_KEY).exists():
        print(f"\n[ERROR] Play service account JSON not found:\n  {JSON_KEY}\n")
        print("Follow these steps to create it:")
        print("  1. Go to https://play.google.com/console → Setup → API access")
        print("  2. Link to a Google Cloud project (or create one)")
        print("  3. Click 'Create new service account'")
        print("  4. In Google Cloud Console: IAM & Admin → Service Accounts →")
        print("     find the account → Keys → Add Key → JSON → download")
        print("  5. Save the JSON file to:")
        print(f"       {JSON_KEY}")
        print("  6. Back in Play Console: Grant the account 'Release manager' role")
        print("  7. Re-run this script")
        sys.exit(1)

def aab_path(ws: str) -> Path:
    return REPO_ROOT / "workspaces" / ws / "android" / "app" / "build" / "outputs" / "bundle" / "release" / "app-release.aab"

def upload_app(app: dict) -> bool:
    """Run fastlane supply for one app. Returns True on success."""
    ws   = app["workspace"]
    name = app["name"]
    pkg  = app["package"]
    aab  = aab_path(ws)
    meta = REPO_ROOT / "workspaces" / ws / "android" / "fastlane" / "metadata" / "android"
    fastlane_dir = REPO_ROOT / "workspaces" / ws / "android"

    banner(f"Uploading: {name}")
    print(f"  Package : {pkg}")
    print(f"  AAB     : {aab}")
    print(f"  Track   : {TRACK}")
    print(f"  Key     : {JSON_KEY}")

    if not aab.exists():
        print(f"\n[SKIP] AAB not found — run bundleRelease first: {aab}")
        return False

    cmd = [
        "fastlane", "supply",
        "--package_name",            pkg,
        "--json_key",                JSON_KEY,
        "--aab",                     str(aab),
        "--track",                   TRACK,
        "--release_status",          "draft",
        "--metadata_path",           str(meta),
        "--skip_upload_images",      "true",
        "--skip_upload_screenshots", "true",
    ]

    print(f"\nRunning: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=str(fastlane_dir))
    if result.returncode == 0:
        print(f"\n[OK] {name} uploaded to Play internal track.")
        return True
    else:
        print(f"\n[FAIL] {name} upload failed (exit {result.returncode}).")
        return False

# ── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    banner("App Factory v2 — Google Play Delivery")
    print(f"Repo  : {REPO_ROOT}")
    print(f"Key   : {JSON_KEY}")
    print(f"Track : {TRACK}")

    check_prerequisites()

    results = {}
    for app in APPS:
        ok = upload_app(app)
        results[app["name"]] = "✅ uploaded" if ok else "❌ failed/skipped"

    banner("Delivery Summary")
    for name, status in results.items():
        print(f"  {status}  {name}")

    print("\nNext step: Go to Play Console → Internal testing → promote to")
    print("           Production when ready (human gate).\n")

if __name__ == "__main__":
    main()
