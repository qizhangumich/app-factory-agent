#!/usr/bin/env python3
"""
App Factory v2 - Play Store Listing Script (Step 2)
====================================================
Uploads store listing metadata, icon, feature graphic and screenshots
to Google Play for all Phase-1 Android apps.

Run AFTER play_deliver.py (Step 1).

Usage:
    python scripts/play_listing.py            # upload metadata + images only
    python scripts/play_listing.py --submit   # also submit for production review

Prerequisites:
  1. config/play_oauth_token.json exists (run play_auth_setup.py once)
  2. Store assets generated (run generate_store_assets.py)
  3. Content rating completed in Play Console UI (once per app, ~5 min)
"""

import json, sys, mimetypes
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()

# GitHub Pages base URL for privacy policies.
# Update GITHUB_USERNAME once repo is on GitHub with Pages enabled.
GITHUB_USERNAME = "linkwave-pte"   # update this
GITHUB_REPO     = "app-factory-agent"
PAGES_BASE      = f"https://{GITHUB_USERNAME}.github.io/{GITHUB_REPO}"

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

SUBMIT_FOR_REVIEW = "--submit" in sys.argv


def banner(msg):
    print(f"\n{'='*60}\n  {msg}\n{'='*60}")


def build_service():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    token_file = REPO_ROOT / "config" / "play_oauth_token.json"
    data  = json.loads(token_file.read_text())
    creds = Credentials(
        token=data["token"], refresh_token=data["refresh_token"],
        token_uri=data["token_uri"], client_id=data["client_id"],
        client_secret=data["client_secret"], scopes=data["scopes"],
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        data["token"] = creds.token
        token_file.write_text(json.dumps(data, indent=2))
    return build("androidpublisher", "v3", credentials=creds, cache_discovery=False)


def meta_dir(ws):
    return REPO_ROOT / "workspaces" / ws / "android" / "fastlane" / "metadata" / "android" / "en-US"

def images_dir(ws):
    return meta_dir(ws) / "images"

def read_text(path):
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""

def privacy_url(ws):
    return f"{PAGES_BASE}/workspaces/{ws}/shared/privacy_policy.html"


def upload_image(service, pkg, edit_id, image_type, image_path):
    """Upload one image to Play Store listing."""
    from googleapiclient.http import MediaFileUpload
    if not image_path.exists():
        print(f"    [skip] {image_path.name} not found")
        return False

    media = MediaFileUpload(str(image_path), mimetype="image/png", resumable=False)
    service.edits().images().upload(
        packageName=pkg,
        editId=edit_id,
        language="en-US",
        imageType=image_type,
        media_body=media,
    ).execute()
    print(f"    [ok] {image_type}: {image_path.name}")
    return True


def upload_app_listing(service, app) -> bool:
    ws   = app["workspace"]
    pkg  = app["package"]
    name = app["name"]
    md   = meta_dir(ws)
    imgs = images_dir(ws)

    banner(f"Listing: {name}")

    title       = read_text(md / "title.txt")
    short_desc  = read_text(md / "short_description.txt")
    full_desc   = read_text(md / "full_description.txt")
    priv_url    = privacy_url(ws)

    print(f"  Title      : {title}")
    print(f"  Privacy URL: {priv_url}")

    try:
        # Open edit
        edit    = service.edits().insert(packageName=pkg, body={}).execute()
        edit_id = edit["id"]

        # 1. Store listing text
        service.edits().listings().update(
            packageName=pkg,
            editId=edit_id,
            language="en-US",
            body={
                "language":         "en-US",
                "title":            title,
                "shortDescription": short_desc,
                "fullDescription":  full_desc,
            }
        ).execute()
        print("  [ok] text metadata uploaded")

        # 2. App details (privacy policy + contact email)
        service.edits().details().update(
            packageName=pkg,
            editId=edit_id,
            body={
                "defaultLanguage": "en-US",
                "contactEmail":    "jeremy4crypto@gmail.com",
                "contactWebsite":  priv_url,
            }
        ).execute()
        print("  [ok] privacy policy + contact email set")

        # 3. Clear existing images then upload fresh ones
        for img_type in ["icon", "featureGraphic", "phoneScreenshots"]:
            try:
                service.edits().images().deleteall(
                    packageName=pkg, editId=edit_id,
                    language="en-US", imageType=img_type
                ).execute()
            except Exception:
                pass

        # Icon 512x512
        upload_image(service, pkg, edit_id, "icon", imgs / "icon.png")

        # Feature graphic 1024x500
        upload_image(service, pkg, edit_id, "featureGraphic", imgs / "feature.png")

        # Screenshots
        for i in range(1, 4):
            upload_image(service, pkg, edit_id, "phoneScreenshots", imgs / f"screen_{i}.png")

        # 4. Optionally promote to production
        if SUBMIT_FOR_REVIEW:
            # Find the latest version code from internal track
            tracks = service.edits().tracks().get(
                packageName=pkg, editId=edit_id, track="internal"
            ).execute()
            releases = tracks.get("releases", [])
            if releases:
                vc = releases[0].get("versionCodes", ["1"])
                service.edits().tracks().update(
                    packageName=pkg, editId=edit_id, track="production",
                    body={"track": "production", "releases": [{
                        "status": "inReview",
                        "versionCodes": vc,
                        "releaseNotes": [{"language": "en-US", "text": "Initial release"}]
                    }]}
                ).execute()
                print("  [ok] submitted for production review")

        # Commit
        service.edits().commit(packageName=pkg, editId=edit_id).execute()
        print(f"  [OK] {name} listing updated")
        return True

    except Exception as e:
        try:
            err = json.loads(e.content)["error"]["message"]
        except Exception:
            err = str(e)
        print(f"  [FAIL] {err}")
        return False


def main():
    banner("App Factory v2 - Play Store Listing (Step 2)")
    submit_msg = " + submit for review" if SUBMIT_FOR_REVIEW else ""
    print(f"Mode: upload metadata + images{submit_msg}")
    print("\nNOTE: Content rating must be completed in Play Console UI before")
    print("      submitting for production review (once per app, ~5 min each).\n")

    service = build_service()
    print("Auth OK\n")

    results = {}
    for app in APPS:
        ok = upload_app_listing(service, app)
        results[app["name"]] = "[OK]" if ok else "[FAIL]"

    banner("Listing Summary")
    for name, status in results.items():
        print(f"  {status}  {name}")

    if not SUBMIT_FOR_REVIEW:
        print("\nTo submit for production review, run:")
        print("  python scripts/play_listing.py --submit")
    print()


if __name__ == "__main__":
    main()
