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
