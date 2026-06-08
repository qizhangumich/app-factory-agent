#!/usr/bin/env python3
"""
App Factory v2 - Master Play Store Release Pipeline
=====================================================
One command, full Android delivery: AAB build -> upload -> listing ->
(optional) production submit. Same template for every app the factory
ships.

Usage:
    python scripts/play_release.py                # full pipeline, internal only
    python scripts/play_release.py --build        # also rebuild AABs first
    python scripts/play_release.py --submit       # also submit to production
    python scripts/play_release.py --build --submit

    python scripts/play_release.py --only ws_002_unitconverterpro
    python scripts/play_release.py --skip-listing  # AAB upload only
    python scripts/play_release.py --skip-deliver  # listing only

Pipeline stages (idempotent — re-run anytime):
    1. Generate store assets   -- skipped if all PNGs already exist
    2. Build signed AABs       -- only if --build is passed
    3. Upload AAB to internal  -- skips apps whose versionCode already
                                  exists on Play
    4. Upload store listing    -- text + icon + feature + screenshots
    5. Submit for review       -- only if --submit is passed
    6. Print content checklist -- reminds about one-time UI clickthrough
"""

import argparse, json, socket, subprocess, sys
from pathlib import Path

socket.setdefaulttimeout(300)

REPO_ROOT  = Path(__file__).parent.parent.resolve()
TOKEN_FILE = REPO_ROOT / "config" / "play_oauth_token.json"

APPS = [
    {
        "name":      "Tip Calculator Deluxe",
        "workspace": "ws_001_tipcalcdeluxe",
        "package":   "com.appfactory.tipcalcdeluxe",
        "slug":      "tipcalcdeluxe",
    },
    {
        "name":      "Unit Converter Pro",
        "workspace": "ws_002_unitconverterpro",
        "package":   "com.appfactory.unitconverterpro",
        "slug":      "unitconverterpro",
    },
    {
        "name":      "QR & Barcode Scanner+",
        "workspace": "ws_004_qrbarcodescanner",
        "package":   "com.appfactory.qrbarcodescanner",
        "slug":      "qrbarcodescanner",
    },
    {
        "name":      "Pomodoro Focus Timer",
        "workspace": "ws_005_pomodorofocus",
        "package":   "com.appfactory.pomodorofocus",
        "slug":      "pomodorofocus",
    },
]

GRADLE = Path.home() / ".gradle/wrapper/dists/gradle-8.7-bin/bhs2wmbdwecv87pi65oeuq5iu/gradle-8.7/bin/gradle"
JAVA_HOME    = "C:/Program Files/Android/Android Studio/jbr"
ANDROID_HOME = "C:/Users/user/AppData/Local/Android/Sdk"

PRIVACY_URL_BASE = "https://qizhangumich.github.io/app-privacy"
DEVELOPER_EMAIL  = "developer_apple@linkwave.one"


# ── Helpers ─────────────────────────────────────────────────────────────────

def banner(msg, char="="):
    bar = char * 70
    print(f"\n{bar}\n  {msg}\n{bar}")

def aab_path(ws):
    return (REPO_ROOT / "workspaces" / ws / "android" /
            "app" / "build" / "outputs" / "bundle" / "release" / "app-release.aab")

def meta_dir(ws):
    return REPO_ROOT / "workspaces" / ws / "android" / "fastlane" / "metadata" / "android" / "en-US"

def images_dir(ws):
    return meta_dir(ws) / "images"

def read_text(path):
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""

def assets_present(ws):
    needed = (
        ["icon.png", "feature.png"]
        + [f"screen_{i}.png"   for i in range(1, 4)]
        + [f"tablet7_{i}.png"  for i in range(1, 4)]
        + [f"tablet10_{i}.png" for i in range(1, 4)]
    )
    return all((images_dir(ws) / n).exists() for n in needed)


# ── Auth ────────────────────────────────────────────────────────────────────

def preflight_checks(apps_to_run):
    """Catch known failure modes before we hit them mid-pipeline."""
    issues = []

    if not TOKEN_FILE.exists():
        issues.append("OAuth token missing — run:  python scripts/play_auth_setup.py")

    # Lesson: superlative claims in descriptions cause "Violation of
    # Metadata policy" rejections (ws_001 "fastest", ws_005 "perfect"
    # rejected 2026-05-27). Run the linter before uploading anything.
    import subprocess
    linter = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "lint_store_metadata.py")],
        capture_output=True, text=True
    )
    if linter.returncode != 0:
        issues.append("Metadata Policy violations found — run "
                      "`python scripts/lint_store_metadata.py` and fix before submit\n"
                      + linter.stdout)

    for app in apps_to_run:
        ws  = app["workspace"]
        kp  = REPO_ROOT / "workspaces" / ws / "android" / "keystore.properties"
        if not kp.exists():
            issues.append(f"{ws}: missing keystore.properties — copy from another workspace, set keyAlias=key1")

    # GitHub Pages reachability — soft check (don't abort if offline)
    try:
        import urllib.request
        for app in apps_to_run[:1]:  # check one URL is enough
            url = f"{PRIVACY_URL_BASE}/{app['slug']}.html"
            urllib.request.urlopen(url, timeout=5)
    except Exception:
        issues.append(f"Privacy policy URL unreachable — verify {PRIVACY_URL_BASE}/<slug>.html  "
                      "(push to .privacy_site repo + enable GitHub Pages)")

    if issues:
        banner("Preflight issues — please fix before continuing", "!")
        for i in issues:
            print(f"  - {i}")
        sys.exit(1)


def build_service():
    if not TOKEN_FILE.exists():
        print(f"\n[ERROR] OAuth token missing: {TOKEN_FILE}")
        print("Run once:  python scripts/play_auth_setup.py")
        sys.exit(1)

    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    data  = json.loads(TOKEN_FILE.read_text())
    creds = Credentials(
        token=data["token"], refresh_token=data["refresh_token"],
        token_uri=data["token_uri"], client_id=data["client_id"],
        client_secret=data["client_secret"], scopes=data["scopes"],
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        data["token"] = creds.token
        TOKEN_FILE.write_text(json.dumps(data, indent=2))

    return build("androidpublisher", "v3", credentials=creds, cache_discovery=False)


# ── Stages ──────────────────────────────────────────────────────────────────

def stage_assets(apps_to_run):
    banner("Stage 1: Store assets", "─")
    missing = [a for a in apps_to_run if not assets_present(a["workspace"])]
    if not missing:
        print("All assets present, skipping.")
        return
    print(f"Generating assets for: {', '.join(a['name'] for a in missing)}")
    # icon + feature graphic only (the marketing-style screens in this
    # script are rejected by Play). Real UI screenshots come from
    # generate_app_screenshots.py.
    subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "generate_store_assets.py")],
                   check=True)
    # Lesson 20d: Play rejects promo-style screenshots. Always produce
    # realistic-UI screenshots after the generic asset pass.
    subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "generate_app_screenshots.py")],
                   check=True)


def stage_build(apps_to_run):
    banner("Stage 2: Build signed AABs", "─")
    env = {"JAVA_HOME": JAVA_HOME, "ANDROID_HOME": ANDROID_HOME, **dict(__import__("os").environ)}
    for app in apps_to_run:
        ws_dir = REPO_ROOT / "workspaces" / app["workspace"] / "android"
        print(f"\n  -> {app['name']}")
        result = subprocess.run(
            [str(GRADLE), "-p", str(ws_dir), ":app:bundleRelease", "-q"],
            env=env, capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"     [OK] {aab_path(app['workspace']).name}")
        else:
            print(f"     [FAIL]\n{result.stderr[-800:]}")


def upload_aab(service, app):
    """Upload AAB to internal track. Returns (success, message)."""
    from googleapiclient.http import MediaFileUpload

    pkg = app["package"]
    aab = aab_path(app["workspace"])
    if not aab.exists():
        return False, f"AAB missing — run with --build"

    try:
        edit    = service.edits().insert(packageName=pkg, body={}).execute()
        edit_id = edit["id"]
        media   = MediaFileUpload(str(aab), mimetype="application/octet-stream",
                                  resumable=True, chunksize=2 * 1024 * 1024)
        req     = service.edits().bundles().upload(
            packageName=pkg, editId=edit_id, media_body=media)

        response = None
        while response is None:
            status, response = req.next_chunk()
            if status:
                print(f"     uploading... {int(status.progress()*100)}%")

        vc = response["versionCode"]
        service.edits().tracks().update(
            packageName=pkg, editId=edit_id, track="internal",
            body={"track": "internal", "releases": [{
                "status": "draft", "versionCodes": [str(vc)],
                "releaseNotes": [{"language": "en-US", "text": "Initial release"}]
            }]}
        ).execute()
        service.edits().commit(packageName=pkg, editId=edit_id).execute()
        return True, f"uploaded versionCode={vc}"

    except Exception as e:
        try:
            err = json.loads(e.content)["error"]["message"]
        except Exception:
            err = str(e)
        return False, err


def stage_deliver(service, apps_to_run):
    banner("Stage 3: Upload AABs to internal track", "─")
    for app in apps_to_run:
        print(f"\n  -> {app['name']}")
        ok, msg = upload_aab(service, app)
        marker = "[OK]" if ok else "[SKIP]" if "already" in msg else "[FAIL]"
        print(f"     {marker} {msg}")


def upload_listing(service, app, submit):
    """Upload listing metadata, images, optionally promote to production."""
    from googleapiclient.http import MediaFileUpload

    pkg = app["package"]
    ws  = app["workspace"]
    md  = meta_dir(ws)
    imgs = images_dir(ws)
    priv_url = f"{PRIVACY_URL_BASE}/{app['slug']}.html"

    try:
        edit    = service.edits().insert(packageName=pkg, body={}).execute()
        edit_id = edit["id"]

        # Lesson #17: remove any rogue language listings (e.g. en-GB that
        # appears empty and blocks "Send for review" with "Some languages
        # have errors"). Only keep en-US until we have real translations.
        try:
            existing = service.edits().listings().list(
                packageName=pkg, editId=edit_id
            ).execute().get("listings", [])
            for l in existing:
                if l["language"] != "en-US":
                    try:
                        service.edits().listings().delete(
                            packageName=pkg, editId=edit_id, language=l["language"]
                        ).execute()
                    except Exception:
                        pass
        except Exception:
            pass

        # text
        service.edits().listings().update(
            packageName=pkg, editId=edit_id, language="en-US",
            body={
                "language":         "en-US",
                "title":            read_text(md / "title.txt"),
                "shortDescription": read_text(md / "short_description.txt"),
                "fullDescription":  read_text(md / "full_description.txt"),
            }
        ).execute()

        # details
        service.edits().details().update(
            packageName=pkg, editId=edit_id,
            body={"defaultLanguage": "en-US", "contactWebsite": priv_url,
                  "contactEmail": DEVELOPER_EMAIL}
        ).execute()

        # clear + re-upload images
        for img_type in ["icon", "featureGraphic", "phoneScreenshots",
                         "sevenInchScreenshots", "tenInchScreenshots"]:
            try:
                service.edits().images().deleteall(
                    packageName=pkg, editId=edit_id,
                    language="en-US", imageType=img_type
                ).execute()
            except Exception:
                pass

        def upload_img(img_type, file_name):
            p = imgs / file_name
            if not p.exists():
                return
            media = MediaFileUpload(str(p), mimetype="image/png", resumable=False)
            service.edits().images().upload(
                packageName=pkg, editId=edit_id, language="en-US",
                imageType=img_type, media_body=media
            ).execute()

        upload_img("icon",            "icon.png")
        upload_img("featureGraphic",  "feature.png")
        for i in range(1, 4):
            upload_img("phoneScreenshots",      f"screen_{i}.png")
            upload_img("sevenInchScreenshots",  f"tablet7_{i}.png")
            upload_img("tenInchScreenshots",    f"tablet10_{i}.png")

        # promote to production if asked
        promoted = False
        if submit:
            tracks = service.edits().tracks().get(
                packageName=pkg, editId=edit_id, track="internal"
            ).execute()
            releases = tracks.get("releases", [])
            if releases:
                vc = releases[0].get("versionCodes", ["1"])
                # Detect if the app has ever been published to production.
                # If not, the API only accepts "draft" status — the human
                # then clicks "Send for review" in Play Console UI once.
                # After that first review, future releases use "completed".
                prod_tracks = service.edits().tracks().get(
                    packageName=pkg, editId=edit_id, track="production"
                ).execute()
                # "ever published" = has a release that left draft state.
                # A draft on production doesn't count — the app is still
                # in "draft app" mode until Play has approved a release.
                ever_published = any(
                    r.get("status") in ("completed", "inProgress", "halted")
                    for r in prod_tracks.get("releases", [])
                )
                status = "completed" if ever_published else "draft"

                service.edits().tracks().update(
                    packageName=pkg, editId=edit_id, track="production",
                    body={"track": "production", "releases": [{
                        "status": status,
                        "versionCodes": vc,
                        "releaseNotes": [{"language": "en-US", "text": "Initial release"}]
                    }]}
                ).execute()
                promoted = status

        # Lesson: after a rejection, the API refuses to send changes for
        # review automatically. Fall back to committing with
        # changesNotSentForReview=true so the edit lands but the human
        # clicks "Send for review" in Play Console UI.
        try:
            service.edits().commit(packageName=pkg, editId=edit_id).execute()
        except Exception as e:
            err = ""
            try: err = json.loads(e.content)["error"]["message"]
            except Exception: err = str(e)
            if "changesNotSentForReview" in err:
                service.edits().commit(
                    packageName=pkg, editId=edit_id,
                    changesNotSentForReview=True
                ).execute()
                return True, "listing updated — click 'Send for review' in Play Console (app had a prior rejection)"
            raise

        if promoted == "completed":
            return True, "submitted for production review (rollout 100%)"
        elif promoted == "draft":
            return True, "production draft created — click 'Send for review' in Play Console"
        return True, "listing updated"

    except Exception as e:
        try:
            err = json.loads(e.content)["error"]["message"]
        except Exception:
            err = str(e)
        return False, err


def stage_listing(service, apps_to_run, submit):
    label = "submit to production" if submit else "internal only"
    banner(f"Stage 4: Upload store listings  ({label})", "─")
    for app in apps_to_run:
        print(f"\n  -> {app['name']}")
        ok, msg = upload_listing(service, app, submit)
        marker = "[OK]" if ok else "[FAIL]"
        print(f"     {marker} {msg}")


def stage_checklist(apps_to_run):
    banner("Stage 5: Content declarations checklist (manual UI)", "─")
    print("These 10 'App content' declarations require Play Console UI clickthrough")
    print("(once per app, ~10 min each). Standard answers in:")
    print("    config/play_content_declarations.yaml")
    print("\nPrint per-app answer sheet:")
    print("    python scripts/print_declarations.py")
    print()
    for app in apps_to_run:
        priv_url = f"{PRIVACY_URL_BASE}/{app['slug']}.html"
        print(f"  {app['name']}")
        print(f"    privacy URL: {priv_url}")


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build",        action="store_true", help="rebuild signed AABs before uploading")
    ap.add_argument("--submit",       action="store_true", help="promote release from internal to production")
    ap.add_argument("--only",         metavar="WORKSPACE", help="run only one workspace (e.g. ws_002_unitconverterpro)")
    ap.add_argument("--skip-deliver", action="store_true", help="skip AAB upload stage")
    ap.add_argument("--skip-listing", action="store_true", help="skip listing upload stage")
    ap.add_argument("--skip-assets",  action="store_true", help="skip asset generation")
    args = ap.parse_args()

    apps_to_run = [a for a in APPS if (args.only is None or a["workspace"] == args.only)]
    if not apps_to_run:
        print(f"No app matches --only {args.only}")
        sys.exit(1)

    banner(f"App Factory v2 — Play Release Pipeline   ({len(apps_to_run)} app(s))")
    print(f"Repo : {REPO_ROOT}")
    print(f"Apps : {', '.join(a['workspace'] for a in apps_to_run)}")
    print(f"Mode : build={args.build}  submit={args.submit}")

    preflight_checks(apps_to_run)

    if not args.skip_assets:
        stage_assets(apps_to_run)
    if args.build:
        stage_build(apps_to_run)

    service = build_service()
    print("\n[auth OK]")

    if not args.skip_deliver:
        stage_deliver(service, apps_to_run)
    if not args.skip_listing:
        stage_listing(service, apps_to_run, args.submit)
    stage_checklist(apps_to_run)

    banner("Pipeline complete")


if __name__ == "__main__":
    main()
