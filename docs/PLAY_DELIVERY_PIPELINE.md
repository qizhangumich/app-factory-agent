# App Factory — Play Delivery Pipeline (Standard Template)

The full Android delivery layer in one document. Same template applies to
every app the factory ever ships — change the APPS list and re-run.

---

## TL;DR — daily command

```bash
# Build, upload AAB to internal, upload listing, print content checklist
python scripts/play_release.py --build
```

Add `--submit` once the per-app content declarations are filled in to
also promote to the production track.

---

## Architecture

```
                         play_release.py (master)
                                  |
        ┌─────────────────┬───────┴────────┬──────────────────┐
        v                 v                v                  v
  generate_store    play_deliver     play_listing      print_declarations
    _assets.py        .py logic        .py logic            .py
        |                 |                |                  |
  icon, feature,     bundleRelease    title, desc,      content rating
  3x screenshots     AAB upload to    images,          answer sheet
  via Playwright     internal track   privacy URL
                                                              ^
                                                              |
                                                config/play_content_
                                                declarations.yaml
```

Every script reads/writes one source of truth — no magic strings.

---

## Files in the pipeline

| Path | Purpose |
|------|---------|
| `scripts/play_release.py` | **Master orchestrator** — runs the full pipeline |
| `scripts/play_deliver.py` | Standalone: build + upload AAB to internal |
| `scripts/play_listing.py` | Standalone: upload listing metadata + images |
| `scripts/play_auth_setup.py` | One-time OAuth2 browser flow |
| `scripts/generate_store_assets.py` | Render store icon/feature/screenshots from SVG |
| `scripts/print_declarations.py` | Print copy-paste content declarations sheet |
| `config/play_content_declarations.yaml` | Canonical answers for the 10 "App content" questions |
| `config/play_oauth_client.json` | OAuth2 client (gitignored) |
| `config/play_oauth_token.json` | OAuth2 refresh token (gitignored) |
| `.privacy_site/` | Working copy of `github.com/qizhangumich/app-privacy` (gitignored) |

---

## One-time setup (per developer machine)

```bash
# 1. Install deps
pip install google-api-python-client google-auth google-auth-oauthlib playwright pillow pyyaml
python -m playwright install chromium

# 2. Create OAuth2 client in Google Cloud Console
#    -> APIs & Services -> Credentials -> Create OAuth client ID
#    -> Application type: Desktop app -> save JSON to config/play_oauth_client.json

# 3. Authorize once (opens browser)
python scripts/play_auth_setup.py
```

Token in `config/play_oauth_token.json` is refreshed automatically;
re-auth only when the refresh token is revoked.

---

## One-time setup (per new app)

For each new app the factory adds:

### 1. Create Play Console listing (~1 min, manual UI)

Play Console -> Create app -> name + package name + Free. Nothing else.

### 2. Fill the 10 "App content" declarations (~10 min, manual UI)

Paste from `python scripts/print_declarations.py <workspace>`. Every
factory app follows the same defaults (no ads, no data collection,
18+, Everyone rating). Save each section.

### 3. Add the app to `APPS` list in `play_release.py`

```python
APPS = [
    ...,
    {
        "name":      "New App Name",
        "workspace": "ws_NNN_slug",
        "package":   "com.appfactory.slug",
        "slug":      "slug",
    },
]
```

(Same dict shape used by `play_deliver.py`, `play_listing.py`, and
`generate_store_assets.py` — add it once, all four scripts pick it up.)

### 4. Add privacy policy HTML

Copy `.privacy_site/_template.html`, save as `.privacy_site/<slug>.html`,
commit + push:

```bash
cd .privacy_site && git add . && git commit -m "add <slug>" && git push
```

GitHub Pages picks it up in 30–90 seconds.

---

## Releasing (per AAB upload — automated)

```bash
python scripts/play_release.py --build
```

Stages:
1. **Assets** — generate Play Store PNGs if missing
2. **Build** — `gradle :app:bundleRelease` for each app
3. **Deliver** — upload signed AAB to `internal` track as draft
4. **Listing** — push title/desc/icon/feature/screenshots
5. **Checklist** — remind which apps still need Play Console UI work

Re-runs are idempotent. `versionCode` already on Play → skipped.

To promote to production review (after content declarations are done
in Play Console UI):

```bash
python scripts/play_release.py --submit
```

---

## Daily workflow

```bash
# bump versionCode in workspaces/ws_XXX/android/app/build.gradle.kts
python scripts/play_release.py --build           # internal release
# verify on physical device via Play internal testing track
python scripts/play_release.py --submit          # promote to production
```

Google review takes 1–3 days for first release per app, hours after that.

---

## What is NOT automated (and why)

| Step | Manual? | Reason |
|------|---------|--------|
| Create app listing in Play Console | Once per app | No Play API endpoint |
| Fill 10 App content declarations | Once per app | No Play API endpoint |
| Promote draft -> live after review approval | 1 click | Intentional human gate |
| Respond to review rejections | Yes | Needs human judgment |

Everything else is API-driven.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `read operation timed out` during AAB upload | Re-run — chunked upload retries automatically. Larger AABs may need `socket.setdefaulttimeout(600)`. |
| `versionCode N has already been used` | Bump `versionCode` in `app/build.gradle.kts` and `--build`. |
| `Package not found` | App listing not created in Play Console UI yet. |
| `Caller does not have permission` | OAuth token expired/revoked — re-run `play_auth_setup.py`. |
| `Privacy policy URL invalid` | GitHub Pages still deploying — wait 60s, re-check `https://qizhangumich.github.io/app-privacy/<slug>.html`. |
| Screenshots/icon wrong style | Edit `APPS` in `generate_store_assets.py`, delete old PNGs, re-run. |
| `Invalid value at 'track_config.releases[0].status' "inReview"` | Pre-v2.4 bug. Status must be `completed` (auto-100%) or `draft`. The current pipeline detects first-vs-subsequent automatically. |
| `Only releases with status draft may be created on draft app` | Brand-new app (never published). Pipeline auto-uses `draft` and prints `click 'Send for review' in Play Console`. |
| `Some languages have errors` | An extra language (often `en-GB`) was added with no content. Remove via `edits().listings().delete(language='en-GB')` — pipeline includes this safeguard. |
| `Add a full description to save` on Main store listing | Tablet screenshots (7" and/or 10") are missing. Run `generate_store_assets.py` then re-run pipeline — generates 1200×1920 and 1600×2560 PNGs. |
| Save button greyed out on Main store listing | UI thinks nothing changed. Add+delete a space in Full description to mark the form dirty, then Save. |
| `Native debug symbols not uploaded` warning | Cosmetic. Apps using ML Kit / CameraX include native .so files. Safe to ignore — doesn't block review. |
| `Violation of Metadata policy` rejection | Description contains a superlative ("fastest", "best", "perfect"), ranking ("#1", "top"), or absolute claim ("ever", "guaranteed"). Run `python scripts/lint_store_metadata.py` to find and fix. Pipeline now runs the linter automatically in preflight. |
| `Changes cannot be sent for review automatically. Please set the query parameter changesNotSentForReview to true` | Triggers after a rejection — Google requires the human to click "Send for review" via UI. Pipeline now retries the commit with that flag set; the human still has to push the button in Play Console. |

---

## Lessons Learned (v2.4)

The hard-won knowledge from the first 4-app delivery to Google Play.
Every item here is encoded somewhere in the pipeline scripts now.

### Auth
1. **Service account keys are blocked** by Google Cloud "Secure by Default"
   even on no-organisation personal projects. Don't waste time on the
   service-account path → use OAuth2 user credentials.
2. **"Setup → API access" is hidden in organisation accounts** in Play
   Console UI. Granting permissions via "Users and permissions" works for
   humans but does NOT grant API access for service accounts.
3. **Enable the Google Play Android Developer API** in the Cloud project
   before any upload, otherwise: `API has not been used... 403`.
4. **OAuth client must be Desktop app type** when creating the OAuth2
   client ID. `play_auth_setup.py` then handles the rest.

### Signing
5. **One upload keystore, one alias, all apps** — pragmatic and avoids
   per-app keystore drift. Our keystore has just `key1`. Per-app
   `keystore.properties` files reference it, never committed.
6. **Sign every release at the Gradle level**, not via Android Studio's
   "Generate Signed Bundle" wizard. The IDE path leaves AABs unsigned in
   `app/build/outputs/bundle/release/` and Play rejects them.

### Build
7. **Bump `versionCode` for every release**. Play API rejects duplicate
   versionCodes with "Version code N has already been used".
8. **Don't trust local Gradle daemons across workspaces** — they cache
   per-project Java config. Run one workspace at a time.

### Upload
9. **Set `socket.setdefaulttimeout(300)`** before any AAB upload. Default
   60s isn't enough even for 3 MB AABs on slow connections.
10. **Use 2 MB chunks** in `MediaFileUpload(chunksize=2*1024*1024)` for
    resumable uploads. Bigger chunks → more timeouts.
11. **The pipeline is idempotent**. Re-runs skip already-uploaded
    versionCodes ("already used") and continue with the rest.

### Listings
12. **Status `"inReview"` is NOT a valid Play API value.** Use:
    - `"completed"` for apps that have been published before (100% rollout)
    - `"draft"` for brand-new apps (forces manual "Send for review" click)
13. **Detect "ever published" correctly**: a release counts only if its
    status is `completed`, `inProgress`, or `halted`. A `draft` release on
    the production track doesn't make the app "published".
14. **First production release of a new app is always a draft.** Google
    requires a human click in Play Console. After approval, future
    releases auto-promote via the API.
15. **Tablet screenshots are REQUIRED** for the Main store listing to pass
    validation. Sizes: 7" = 1200×1920, 10" = 1600×2560. Chromebook and
    Android XR screenshots remain optional.
16. **API upload alone doesn't mark the listing as "saved"**. Play Console
    UI requires a human click on **Save** at the Main store listing page.
    Workaround: add+delete a space in Full description to enable Save.
17. **Languages**: stick to `en-US` only at launch. Adding an empty
    language (e.g. `en-GB` accidentally) triggers "Some languages have
    errors" and blocks Send for review. Remove with
    `edits().listings().delete(language='en-GB')`.

### Privacy policies
18. **Privacy policies must be publicly accessible HTML URLs.** GitHub
    Pages works once the repo is pushed (first deployment 1-5 min).
19. **Set both `contactWebsite` and `contactEmail`** via `edits().details().update()`. Play also reads `contactWebsite` as the
    privacy policy URL when the dedicated field is blank.
20. **Privacy file slug must match the app's slug.** Use a single source
    of truth (the slug in `APPS` list).
20a. **Privacy policy MUST name the publishing entity** (e.g. "LINKWAVE
    PTE.LTD.") and the app by name, with a working contact email.
    Generic "App Factory" / placeholder emails will be rejected during
    review. Generator at `scripts/generate_privacy_policies.py`.

### Metadata policy (description text)
20b. **Description text MUST NOT contain superlatives, rankings, or
    awards.** Google rejected the first batch because "The fastest way
    to split any bill" appears in ws_001's description. Other banned
    words seen in our content: "best", "perfect", "ever" (in
    "best ever", "no ads ever"). The factory's `scripts/lint_store_metadata.py` enforces this; it now runs as a
    preflight gate in `play_release.py`, so a description containing a
    banned phrase aborts the pipeline before any API call.
20c. **After a rejection, `edits.commit()` rejects automatic
    resubmission** with "Changes cannot be sent for review
    automatically." The pipeline retries the commit with
    `changesNotSentForReview=true` so the edit lands; the human then
    clicks "Send for review" once in Play Console UI.

### Content declarations (the 10/11 manual checklist)
21. **No API for**: content rating questionnaire, target audience, data
    safety, ads, app access, government, financial, special categories.
    These are UI-only and require the once-per-app manual clickthrough.
22. **Standard answers** for every factory app live in
    `config/play_content_declarations.yaml`. Per-app deviations go in the
    `overrides:` section. `print_declarations.py` emits a copy-paste sheet.
23. **App content section count = 11**, not 10. Health is its own
    section, separate from "special categories".

### Final manual steps (one-time per new app)
24. **Countries/regions must be selected manually** on the Production
    track before Send for review. No API endpoint for this.
25. **Click "Send N changes for review"** on the Publishing overview page
    after the dashboard shows all green ✅. This is the actual Google
    review submission.
26. **Native debug symbol warning is safe to ignore** for first release.
    Apps using ML Kit / CameraX include `.so` files but absence of debug
    symbols only affects crash report readability.

### Workflow
27. **`--only ws_NNN_slug`** ships one app at a time — useful for
    debugging or staged rollouts.
28. **`--skip-deliver`**, **`--skip-listing`**, **`--skip-assets`** skip
    individual stages when you only want to update one slice.
29. **Once an app is approved**, future updates skip ALL the manual UI
    steps (declarations, store listing save, send-for-review). Just bump
    versionCode and re-run.
