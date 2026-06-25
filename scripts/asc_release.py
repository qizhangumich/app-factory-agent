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

import argparse, hashlib, json, sys
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

# Map our local screenshot file prefix -> Apple's screenshotDisplayType
# enum value. The pixel dimensions are validated by Apple at upload.
IOS_SCREENSHOT_TYPES = {
    "iphone_6_7": "APP_IPHONE_67",
    "ipad_12_9":  "APP_IPAD_PRO_3GEN_129",
}


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


def latest_valid_build(token, app_id):
    """Return the build id of the most recent processed/valid build,
    or None if none exists."""
    r = asc_request("GET", token,
                    f"/builds?filter[app]={app_id}&limit=20")
    if r.status_code != 200:
        return None
    candidates = []
    for b in r.json().get("data", []):
        a = b["attributes"]
        if a.get("processingState") == "VALID" and not a.get("expired"):
            candidates.append((a.get("uploadedDate", ""), b["id"]))
    candidates.sort(reverse=True)
    return candidates[0][1] if candidates else None


def attach_build_to_version(token, version_id, build_id):
    body = {
        "data": {
            "type": "builds",
            "id":   build_id,
        }
    }
    # Use relationship-update endpoint to attach the build.
    r = asc_request("PATCH", token,
                    f"/appStoreVersions/{version_id}/relationships/build",
                    body=body)
    return r.status_code in (200, 204), r


def set_categories(token, app_info_id, primary_id, secondary_id=None):
    """Set primary + secondary categories on the AppInfo.

    Apple rejects both PATCH attrs and PATCH /relationships/<name>
    for categories. The only form that works is PATCH /appInfos/{id}
    with the categories supplied as relationships inside the data
    block — even though the API docs imply otherwise.
    """
    relationships = {
        "primaryCategory": {
            "data": {"type": "appCategories", "id": primary_id}
        }
    }
    if secondary_id:
        relationships["secondaryCategory"] = {
            "data": {"type": "appCategories", "id": secondary_id}
        }
    body = {
        "data": {
            "type":          "appInfos",
            "id":            app_info_id,
            "relationships": relationships,
        }
    }
    r = asc_request("PATCH", token, f"/appInfos/{app_info_id}", body=body)
    return r.status_code == 200


def set_content_rights_declaration(token, app_id):
    """App needs contentRightsDeclaration. We don't use any third-party
    content in our utility apps, so the value is always
    DOES_NOT_USE_THIRD_PARTY_CONTENT."""
    body = {
        "data": {
            "type": "apps",
            "id":   app_id,
            "attributes": {
                "contentRightsDeclaration": "DOES_NOT_USE_THIRD_PARTY_CONTENT"
            }
        }
    }
    r = asc_request("PATCH", token, f"/apps/{app_id}", body=body)
    return r.status_code == 200


def set_build_export_compliance(token, build_id):
    """Build needs usesNonExemptEncryption set. Our Info.plist already
    declares ITSAppUsesNonExemptEncryption=NO, but Apple still wants the
    attribute set on the Build resource directly. Always false for our
    utility apps (only standard HTTPS, exempt)."""
    body = {
        "data": {
            "type": "builds",
            "id":   build_id,
            "attributes": {"usesNonExemptEncryption": False}
        }
    }
    r = asc_request("PATCH", token, f"/builds/{build_id}", body=body)
    return r.status_code == 200


def ensure_free_price_schedule(token, app_id):
    """Set the app's price schedule to Free if not already set.
    Apple's submit gate requires a price schedule even for free apps.

    Uses the v1/appPriceSchedules endpoint with USA as the base
    territory and the USA $0.00 price point. Each app has its own
    encoded price point ids, so we look it up at runtime.

    Idempotent: if a schedule already exists, GET returns 200 with the
    existing data and we skip.
    """
    # Check if a schedule already exists (schedule id == app id by Apple's design)
    r = asc_request("GET", token, f"/appPriceSchedules/{app_id}")
    if r.status_code == 200:
        return True

    # Look up the USA free price point for this app
    r = asc_request("GET", token,
                    f"/apps/{app_id}/appPricePoints?filter[territory]=USA&limit=5")
    if r.status_code != 200:
        return False
    free_pp_id = None
    for p in r.json().get("data", []):
        price = p["attributes"].get("customerPrice")
        # "0.0", "0.00", "0", 0 — all mean free
        if str(price).strip() in ("0", "0.0", "0.00"):
            free_pp_id = p["id"]
            break
    if not free_pp_id:
        return False

    body = {
        "data": {
            "type": "appPriceSchedules",
            "relationships": {
                "app":           {"data": {"type": "apps",       "id": app_id}},
                "baseTerritory": {"data": {"type": "territories", "id": "USA"}},
                "manualPrices":  {"data": [{"type": "appPrices", "id": "${free-now}"}]},
            },
        },
        "included": [
            {
                "type": "appPrices",
                "id":   "${free-now}",
                "attributes": {"startDate": None},
                "relationships": {
                    "appPricePoint": {
                        "data": {"type": "appPricePoints", "id": free_pp_id}
                    },
                    "territory": {
                        "data": {"type": "territories", "id": "USA"}
                    },
                },
            }
        ],
    }
    r = asc_request("POST", token, "/appPriceSchedules", body=body)
    return r.status_code == 201


def set_version_copyright_and_review(token, version_id, copyright_str,
                                      contact_email, contact_name="LINKWAVE Support",
                                      contact_phone="+65 0000 0000"):
    """Two related fields on the AppStoreVersion that submit requires:
      - copyright attribute
      - appStoreReviewDetail relationship (reviewer-contact info)
    """
    # 1. copyright
    body = {
        "data": {
            "type": "appStoreVersions",
            "id":   version_id,
            "attributes": {"copyright": copyright_str},
        }
    }
    r = asc_request("PATCH", token, f"/appStoreVersions/{version_id}", body=body)
    cop_ok = r.status_code == 200

    # 2. appStoreReviewDetail (find or create)
    r = asc_request("GET", token,
                    f"/appStoreVersions/{version_id}/appStoreReviewDetail")
    if r.status_code == 200 and r.json().get("data"):
        rev_ok = True   # already exists
    else:
        first, last = contact_name.split(" ", 1) if " " in contact_name else (contact_name, "")
        body = {
            "data": {
                "type": "appStoreReviewDetails",
                "attributes": {
                    "contactFirstName":     first,
                    "contactLastName":      last,
                    "contactEmail":         contact_email,
                    "contactPhone":         contact_phone,
                    "demoAccountRequired":  False,
                },
                "relationships": {
                    "appStoreVersion": {
                        "data": {"type": "appStoreVersions", "id": version_id}
                    }
                }
            }
        }
        r = asc_request("POST", token, "/appStoreReviewDetails", body=body)
        rev_ok = r.status_code == 201

    return cop_ok and rev_ok


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


# ── Screenshot upload (Apple's reserve-then-PUT chunked protocol) ──────────

def list_screenshot_sets(token, version_loc_id):
    r = asc_request("GET", token,
                    f"/appStoreVersionLocalizations/{version_loc_id}/appScreenshotSets")
    if r.status_code != 200:
        return {}
    return {
        s["attributes"]["screenshotDisplayType"]: s["id"]
        for s in r.json().get("data", [])
    }


def create_screenshot_set(token, version_loc_id, display_type):
    body = {
        "data": {
            "type": "appScreenshotSets",
            "attributes": {"screenshotDisplayType": display_type},
            "relationships": {
                "appStoreVersionLocalization": {
                    "data": {"type": "appStoreVersionLocalizations",
                             "id": version_loc_id}
                }
            }
        }
    }
    r = asc_request("POST", token, "/appScreenshotSets", body=body)
    if r.status_code == 201:
        return r.json()["data"]["id"]
    return None


def delete_screenshots_in_set(token, set_id):
    """Clear any existing screenshots in the set so we can re-upload."""
    r = asc_request("GET", token, f"/appScreenshotSets/{set_id}/appScreenshots")
    if r.status_code != 200:
        return
    for s in r.json().get("data", []):
        asc_request("DELETE", token, f"/appScreenshots/{s['id']}")


def upload_one_screenshot(token, set_id, png_path: Path) -> bool:
    """Reserve → PUT → commit, per Apple's chunked upload protocol."""
    import requests
    file_bytes = png_path.read_bytes()
    file_size  = len(file_bytes)
    md5_hex    = hashlib.md5(file_bytes).hexdigest()

    # 1) Reserve
    body = {
        "data": {
            "type": "appScreenshots",
            "attributes": {"fileSize": file_size, "fileName": png_path.name},
            "relationships": {
                "appScreenshotSet": {
                    "data": {"type": "appScreenshotSets", "id": set_id}
                }
            }
        }
    }
    r = asc_request("POST", token, "/appScreenshots", body=body)
    if r.status_code != 201:
        try:
            err = r.json().get("errors", [{}])[0].get("detail", r.text[:200])
        except Exception:
            err = r.text[:200]
        print(f"      [reserve fail] {err}")
        return False

    data = r.json()["data"]
    sid  = data["id"]
    ops  = data["attributes"].get("uploadOperations", [])

    # 2) PUT each chunk
    for op in ops:
        method  = op.get("method", "PUT")
        url     = op["url"]
        headers = {h["name"]: h["value"] for h in op.get("requestHeaders", [])}
        offset  = op.get("offset", 0)
        length  = op.get("length", file_size)
        chunk   = file_bytes[offset : offset + length]
        try:
            rr = requests.request(method, url, headers=headers, data=chunk, timeout=120)
            if rr.status_code not in (200, 201, 204):
                print(f"      [PUT fail HTTP {rr.status_code}] {rr.text[:200]}")
                return False
        except Exception as e:
            print(f"      [PUT exception] {e}")
            return False

    # 3) Commit
    commit_body = {
        "data": {
            "type": "appScreenshots",
            "id":   sid,
            "attributes": {"uploaded": True, "sourceFileChecksum": md5_hex},
        }
    }
    r = asc_request("PATCH", token, f"/appScreenshots/{sid}", body=commit_body)
    return r.status_code == 200


def upload_screenshots_for_app(token, version_loc_id, ws):
    """Walk workspaces/<ws>/ios/fastlane/screenshots/en-US/* and upload
    each PNG to the matching screenshot set. Replaces any existing
    screenshots in the set so re-runs are idempotent."""
    src_dir = (REPO_ROOT / "workspaces" / ws / "ios" / "fastlane"
               / "screenshots" / "en-US")
    if not src_dir.exists():
        print(f"      [skip screenshots] no folder {src_dir}")
        return

    existing_sets = list_screenshot_sets(token, version_loc_id)

    # Group files by display type prefix
    by_type = {}
    for png in sorted(src_dir.glob("*.png")):
        # filename pattern: <prefix>_<n>.png  where prefix matches IOS_SCREENSHOT_TYPES
        for prefix, display_type in IOS_SCREENSHOT_TYPES.items():
            if png.name.startswith(prefix + "_"):
                by_type.setdefault(display_type, []).append(png)
                break

    for display_type, files in by_type.items():
        set_id = existing_sets.get(display_type)
        if not set_id:
            set_id = create_screenshot_set(token, version_loc_id, display_type)
            if not set_id:
                print(f"      [skip {display_type}] set create failed")
                continue
        else:
            delete_screenshots_in_set(token, set_id)

        print(f"      {display_type}: uploading {len(files)} file(s)...")
        for png in files:
            ok = upload_one_screenshot(token, set_id, png)
            print(f"        {'[ok]' if ok else '[FAIL]'} {png.name}")


def submit_for_review(token, app_id, version_id, dry_run=False):
    """Submit a version using Apple's modern ReviewSubmission flow.
    Apple deprecated the older appStoreVersionSubmissions endpoint
    (now DELETE-only) in favor of reviewSubmissions which can bundle
    multiple items (versions, IAPs) into a single review.

    Steps:
      1. POST /v1/reviewSubmissions  → creates an in-progress submission
      2. POST /v1/reviewSubmissionItems  → attach the version
      3. PATCH /v1/reviewSubmissions/{id} {submitted: true}  → send to Apple
    """
    if dry_run:
        return True, "DRY_RUN"

    # 1. Look for an existing draft submission (state can be IN_PROGRESS
    # or READY_FOR_REVIEW depending on whether items have been attached).
    # Reuse one with no items; delete orphaned ones with no items only if
    # we end up creating a new submission anyway (avoid leaving more
    # orphans behind on subsequent runs).
    r = asc_request("GET", token,
                    f"/reviewSubmissions?filter[app]={app_id}&limit=20")
    submission_id = None
    candidates = []
    if r.status_code == 200:
        for s in r.json().get("data", []):
            state = s["attributes"].get("state", "")
            if state in ("IN_PROGRESS", "READY_FOR_REVIEW"):
                candidates.append(s["id"])
    # Pick the first one (we'll attach our version to it)
    if candidates:
        submission_id = candidates[0]

    if not submission_id:
        body = {
            "data": {
                "type": "reviewSubmissions",
                "attributes": {"platform": "IOS"},
                "relationships": {
                    "app": {"data": {"type": "apps", "id": app_id}}
                }
            }
        }
        r = asc_request("POST", token, "/reviewSubmissions", body=body)
        if r.status_code != 201:
            try:
                detail = r.json()["errors"][0].get("detail", r.text[:300])
            except Exception:
                detail = r.text[:300]
            return False, f"create reviewSubmission HTTP {r.status_code}: {detail}"
        submission_id = r.json()["data"]["id"]

    # 2. Attach the version (skip if already attached)
    r = asc_request("GET", token,
                    f"/reviewSubmissions/{submission_id}/items")
    already_attached = False
    if r.status_code == 200:
        for item in r.json().get("data", []):
            rel = item.get("relationships", {}).get("appStoreVersion", {}).get("data") or {}
            if rel.get("id") == version_id:
                already_attached = True
                break

    if not already_attached:
        item_body = {
            "data": {
                "type": "reviewSubmissionItems",
                "relationships": {
                    "reviewSubmission": {
                        "data": {"type": "reviewSubmissions", "id": submission_id}
                    },
                    "appStoreVersion": {
                        "data": {"type": "appStoreVersions", "id": version_id}
                    }
                }
            }
        }
        r = asc_request("POST", token, "/reviewSubmissionItems", body=item_body)
        if r.status_code != 201:
            try:
                detail = r.json()["errors"][0].get("detail", r.text[:300])
            except Exception:
                detail = r.text[:300]
            return False, f"attach version HTTP {r.status_code}: {detail}"

    # 3. Submit
    submit_body = {
        "data": {
            "type": "reviewSubmissions",
            "id":   submission_id,
            "attributes": {"submitted": True},
        }
    }
    r = asc_request("PATCH", token,
                    f"/reviewSubmissions/{submission_id}", body=submit_body)
    if r.status_code == 200:
        return True, submission_id
    try:
        detail = r.json()["errors"][0].get("detail", r.text[:300])
    except Exception:
        detail = r.text[:300]
    return False, f"submit PATCH HTTP {r.status_code}: {detail}"


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


def release_one(token, app, common, submit=False, dry_run=False, upload_screens=False):
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
        # Categories must be set via the relationships endpoint — the
        # attribute form returns 200 but doesn't actually update anything.
        cat_ok = set_categories(
            token, info_id,
            primary_id=app["category_primary"],
            secondary_id=app.get("category_secondary"),
        )
        print(f"  categories:        {'OK' if cat_ok else 'FAIL'}")

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

    # 3a. Attach the latest valid build to the version. Required before
    # submission; without a build the version is unreleasable.
    build_id = latest_valid_build(token, app_id)
    if build_id and not dry_run:
        ok, r = attach_build_to_version(token, version_id, build_id)
        print(f"  attach build:      {'OK' if ok else 'FAIL'}  build={build_id}")
        # Build needs usesNonExemptEncryption set on the resource itself.
        ok = set_build_export_compliance(token, build_id)
        print(f"  build encryption:  {'OK' if ok else 'FAIL'}")
    elif not build_id:
        print(f"  attach build:      [skip] no VALID build yet — wait for TestFlight processing")

    # 3b. App-level content rights declaration + price schedule (free)
    if not dry_run:
        ok = set_content_rights_declaration(token, app_id)
        print(f"  content rights:    {'OK' if ok else 'FAIL'}")
        ok = ensure_free_price_schedule(token, app_id)
        print(f"  pricing (free):    {'OK' if ok else 'FAIL'}")

    # 3c. Version copyright + reviewer contact info
    if not dry_run:
        ok = set_version_copyright_and_review(
            token, version_id,
            copyright_str=common["copyright"],
            contact_email=common.get("contact_email", "developer_apple@linkwave.one"),
            contact_name=common.get("contact_name", "LINKWAVE Support"),
            contact_phone=common.get("contact_phone", "+6581234567"),
        )
        print(f"  copyright/review:  {'OK' if ok else 'FAIL'}")

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

        # Screenshot upload (chunked protocol)
        if upload_screens:
            print(f"  screenshots:")
            upload_screenshots_for_app(token, vloc_id, ws)

    # 5. Optional submit (uses modern reviewSubmissions flow)
    if submit:
        ok, detail = submit_for_review(token, app_id, version_id)
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
    ap.add_argument("--screenshots", action="store_true",
                    help="also upload screenshots from "
                         "workspaces/<ws>/ios/fastlane/screenshots/en-US/")
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
                                    submit=args.submit, dry_run=args.dry_run,
                                    upload_screens=args.screenshots))

    # Summary
    print("\n" + "=" * 60)
    print(f"{'Workspace':30} Status")
    print("=" * 60)
    for r in results:
        print(f"{r['workspace']:30} {r['status']}  {r.get('msg','')}")


if __name__ == "__main__":
    main()
