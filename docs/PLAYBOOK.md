# App Factory v2 — Playbook

> **Pitch:** A small Python repo turns one human + an LLM into a 2-store
> publishing pipeline. From spec → signed binary → public listing → review
> queue — in **one command per release**, on **both Android and iOS**.
>
> **Goal of this document:** an undergrad can read it in an afternoon
> and ship their own app to both stores in the same day.

---

## 1. What we proved

Phase 1, 5 apps, ~3 calendar days of human time over 4 weeks:

| | Android | iOS |
|---|---------|-----|
| Apps shipped to review | 4 / 4 | 5 / 5 |
| Apps approved & live | 4 / 4 | (in review) |
| Human web-UI clicks per release | **0** | **0** |
| Human web-UI clicks per **new app**, one-time | ~11 min | ~2 min + Apple's required "App Privacy" Q |
| Lines of code (factory) | 5 492 |
| External deps (per release) | Gradle, Playwright, Apple ASC API, Google Play API | + Xcode 26 on a GitHub macOS runner |

The artifact that makes this possible is **the methodology**, not the
apps. The apps are the proof.

---

## 2. The 5-layer architecture

```
                              ┌──────────────────────────┐
                              │  Layer 1: BRAIN          │  decisions
                              │  brain/*.py              │  what to ship,
                              │  (market_scanner,        │  to whom,
                              │   app_scorer,            │  at what price
                              │   pricing_optimizer,     │
                              │   kill_boost, …)         │
                              └────────────┬─────────────┘
                                           │ spec.json
                                           ▼
                              ┌──────────────────────────┐
                              │  Layer 2: FACTORY        │  write code
                              │  Claude Code workers     │  (Swift,
                              │  per spec.json           │   Kotlin,
                              │  → workspaces/ws_NNN_*/  │   XML, plist)
                              └────────────┬─────────────┘
                                           │ source tree
                                           ▼
                              ┌──────────────────────────┐
                              │  Layer 2.5: BUILD &      │  compile, fix,
                              │  FINE-TUNE               │  verify on
                              │  Gradle / Xcode CI       │  device, sign
                              │  (most lessons here)     │
                              └────────────┬─────────────┘
                                           │ signed .aab / .ipa
                                           ▼
                              ┌──────────────────────────┐
                              │  Layer 3: DELIVERY       │  upload, list,
                              │  scripts/{play,asc}_*.py │  screenshots,
                              │  + Apple/Google APIs     │  submit
                              └────────────┬─────────────┘
                                           │ in store review
                                           ▼
                              ┌──────────────────────────┐
                              │  Layer 4: HUMAN GATE     │  click "Send for
                              │  (~5% of work)           │  Review" / answer
                              │                          │  questionnaire
                              └──────────────────────────┘
```

Each layer has **one job**, **one config**, and **one entry-point script**.
The contract between layers is a folder structure (`workspaces/ws_NNN_slug/`)
plus a small JSON manifest. Nothing else.

---

## 3. The repo layout (it's the API)

```
.
├── brain/                       Layer 1 — decision engine (Python stdlib only)
│   ├── market_scanner.py        backlog of app ideas
│   ├── app_scorer.py            score each idea on size × risk × moat
│   ├── platform_router.py       iOS-only? Android-only? both?
│   ├── account_manager.py       account ↔ category mapping
│   ├── pricing_optimizer.py     paid vs free vs $0.99 by category
│   ├── kill_boost.py            cut losers, double down on winners
│   ├── localization_planner.py  which languages to add when
│   ├── revenue_tracker.py       roll-up of all apps' ledgers
│   ├── platform_router.py       picks the right pipeline
│   └── state_io.py              shared JSON read/write
│
├── factory/                     Layer 2 — queue manager (TBD; today driven by
│                                Claude Code directly per spec.json)
│
├── workspaces/                  Layer 2-output / 2.5-input / 3-input
│   └── ws_NNN_slug/             one app = one folder, fully isolated
│       ├── spec.json            brain's instructions for the factory
│       ├── workspace.json       lifecycle state + bundle ids
│       ├── status.json          last brain decision
│       ├── shared/              app_icon.svg, privacy_policy.html, …
│       ├── android/             Android Studio project, fastlane metadata
│       ├── ios/                 Xcode project, fastlane screenshots
│       └── LAUNCH_CHECKLIST.md  auto-generated per-app launch cheat sheet
│
├── scripts/                     Layer 3 — the only thing the human runs
│   ├── play_release.py          Android: build → upload → list → submit
│   ├── asc_release.py           iOS:     metadata → screenshots → submit
│   ├── asc_status.py            review dashboard
│   ├── generate_*_screenshots.py
│   ├── lint_store_metadata.py   pre-flight: no banned superlatives
│   └── fix_ios_*.py             one-shot pbxproj / Info.plist patchers
│
├── config/
│   ├── play_content_declarations.yaml   standard Play "App content" answers
│   ├── ios_app_metadata.yaml            per-app iOS store metadata
│   ├── ios_apps.yaml                    bundle IDs + name fallback lists
│   ├── accounts_config.yaml             account ↔ category mapping
│   └── asc_api_key.json (gitignored)    ASC API credentials
│
├── delivery/
│   └── fastlane/                Fastfile + Matchfile (iOS signing)
│
├── .github/workflows/
│   ├── android_deploy.yml       (local Gradle is faster; this is fallback)
│   └── ios_deploy.yml           macOS-15 runner + match + gym + deliver
│
├── docs/                        the runbooks (you are here)
│   ├── PLAYBOOK.md              ← this file (start here)
│   ├── PLAY_DELIVERY_PIPELINE.md  Android-specific gotchas
│   ├── OPERATIONS.md            one-time setup
│   └── ANDROID_SHIPPING.md      ramp-up reference
│
└── instructions/
    └── APP_FACTORY_INSTRUCTION_BOOK_V2.md   the original brain spec
```

---

## 4. Day-1 curriculum: 7 hours, undergraduate-shippable

A student who finishes this list will have submitted a real app to both
stores by the end of the day.

| Hour | What they do | What they read |
|------|--------------|----------------|
| **1** | Clone repo, run `pip install -r requirements.txt`, scan `docs/PLAYBOOK.md` (this file). Sign up for Apple Developer ($99) and Google Play Console ($25) accounts. | This file, §1–§4. |
| **2** | Read `instructions/APP_FACTORY_INSTRUCTION_BOOK_V2.md` end to end. It's the long-form rationale. | The brain. |
| **3** | Walk through one existing app, e.g. `workspaces/ws_001_tipcalcdeluxe/`. Open `spec.json`, the Kotlin source, the Swift source, the per-platform `fastlane/` folders. Run `python scripts/asc_status.py` to see Apple's live state. | Open `LAUNCH_CHECKLIST.md` in that workspace. |
| **4** | Build one app **locally**. Android: `gradle :app:bundleRelease` in `workspaces/ws_001/android`. iOS: open `.xcodeproj`, hit ⌘B. | `docs/ANDROID_SHIPPING.md` |
| **5** | Set up credentials: ASC API key (4 secrets), Google Play OAuth (1 file), match repo (1 PAT). Run `python scripts/asc_register_apps.py` for a new bundle ID; create the app entry in App Store Connect web UI. | `docs/OPERATIONS.md` + §6 below |
| **6** | Write a new spec.json for your own app (small utility — pick from `brain/market_scanner.py`'s backlog if stuck). Run the Layer 2 step manually (cursor / Claude Code generates Kotlin + Swift to the workspace). | This doc §7. |
| **7** | Run the full delivery: `python scripts/play_release.py --build --submit` (Android) and trigger `ios_deploy.yml` then `python scripts/asc_release.py --submit --screenshots` (iOS). Email Apple/Google when their queue notifications hit your inbox. | §8 below. |

At hour 7 the student has a binary in **both** review queues and knows
which command to run to ship #2.

---

## 5. Daily ops cheat sheet

The whole factory in 6 commands. Memorize these.

```bash
# Add an iOS bundle id + auto-rename to a free App Store name
python scripts/asc_register_apps.py

# Build + upload a signed Android AAB to Play (internal track first)
python scripts/play_release.py --build --submit

# Trigger iOS build on GitHub's macOS runner
gh workflow run ios_deploy.yml -f workspace=ws_NNN_slug   # or via web UI

# After the .ipa is processed in TestFlight (~10 min): push iOS metadata + submit
python scripts/asc_release.py --submit --screenshots --only ws_NNN_slug

# Live dashboard — every app's review state from both stores
python scripts/asc_status.py

# When you change app behavior and need to bump the build for re-submit
# (versionCode for Android is in build.gradle.kts; iOS auto-bumps via epoch sec)
python scripts/play_release.py --build --submit
```

That's the whole job.

---

## 6. Per-new-app workflow — 11 min total human time

Everything below this line is the **one-time** cost of admitting a
brand new app into the factory. After the first approved release,
future updates take **zero human clicks**.

| # | Step | Where | Time |
|---|------|-------|------|
| 1 | Drop a `spec.json` in a new `workspaces/ws_NNN_slug/` | local | 2 min |
| 2 | Layer 2 generates Kotlin + Swift code (Claude Code, current operator) | local | runs unattended |
| 3 | First local build to shake out compile errors | local | 5 min |
| 4 | Create the Android app listing in Play Console | play.google.com/console | 1 min |
| 5 | Fill 11 Play "App content" declarations (paste from `scripts/print_declarations.py`) | play.google.com/console | 10 min one-time |
| 6 | Run `scripts/asc_register_apps.py` (auto-creates iOS bundle id, then asks you to create the App Store entry shell) | local + ASC web | 1 min |
| 7 | Answer Apple's "App Privacy → No data collected" prompt | ASC web UI | 30 sec |
| 8 | `python scripts/play_release.py --build --submit` | local | 1 command |
| 9 | Trigger `ios_deploy.yml` | GitHub | 1 click |
| 10 | `python scripts/asc_release.py --submit --screenshots` | local | 1 command |

If a student gets to step 10, the app is in **both** review queues.

---

## 7. The "spec.json" contract — what you write to define a new app

```jsonc
// workspaces/ws_NNN_slug/spec.json
{
  "name":              "Tip Calc Deluxe",          // user-visible app name
  "slug":              "tipcalcdeluxe",            // url-safe; matches folder
  "bundle_id_android": "com.appfactory.tipcalcdeluxe",
  "bundle_id_ios":     "com.linkwave.tipcalcdeluxe",
  "category":          "tools",                    // see config/genre_map.json
  "one_liner":         "Split bills clean & fast.",
  "core_features": [
    "custom tip slider (0–50%)",
    "split 1–20 people",
    "history of last 20 calculations"
  ],
  "permissions":   [],                             // no camera/mic/location
  "monetization":  "free",                         // free | iap | paid_099
  "platforms":     ["android", "ios"],
  "brain_score":   72,                             // app_scorer output (0–100)
  "brain_reason":  "TAM=high (everyone), competition=high, our edge=clean UI"
}
```

The factory reads this file, generates ~30 source files, and produces
a working app. Everything else flows from this contract.

---

## 8. Lessons learned — the catalog

These are the gotchas that cost us hours each. They're now encoded in
the scripts as comments, but here's the single-page index so you can
search before debugging.

### Google Play (28 lessons in `docs/PLAY_DELIVERY_PIPELINE.md`)
1. Service-account JSON auth is blocked by Cloud's Secure-by-Default policy → use OAuth2 user creds
2. "Setup → API access" is hidden on org Play Console accounts
3. Tablet screenshots are required, not phone-only
4. Brand-new apps must use "draft" status on first production release (Google adds a forced human click)
5. Screenshots must show actual app UI, not promo graphics (Metadata Policy rejection)
6. Privacy policy URL must name the publisher entity ("LINKWAVE PTE.LTD.")
7. Metadata Policy bans every superlative — "fastest", "best", "ever", "perfect", etc. (`lint_store_metadata.py` catches them pre-flight)
8. Empty `en-GB` language listing breaks "Send for review" — strip non-en-US listings
9. The 11 "App content" declarations are web-UI only — no API
10. Re-running a rejected workflow re-uses the **failed commit**, not main — always start a fresh run after a code fix

### App Store Connect (15 lessons in `scripts/asc_release.py` comments)
1. `POST /apps` is **removed** — create the app entry in the web UI (Apple anti-spam)
2. App name lives on `AppInfoLocalization`, not on the App resource itself
3. Categories: PATCH `/appInfos/{id}` with categories **as relationships in the data block** (not `/relationships/primaryCategory`)
4. `usesNonExemptEncryption` must be set on the **Build** resource even when `ITSAppUsesNonExemptEncryption=NO` is in `Info.plist`
5. Reviewer phone must be a real-looking E.164 number; all-zero placeholders fail
6. **Free apps need a price schedule** with the USA $0 price point — there's no "no pricing" state
7. Age rating dimensions are a **mix of BOOLEAN and STRING** types and the bucketing shifts; auto-detect from the API's type-mismatch errors and retry
8. **App Privacy** ("data collected" nutrition label) is web-UI-only — no public API
9. The `reviewSubmissions` flow (2023+) replaced the old `appStoreVersionSubmissions`: create, attach items, PATCH `submitted=true`
10. `CFBundleVersion` must be > previous TestFlight upload — `increment_build_number` with `Time.now.to_i`
11. Match needs a private repo + `MATCH_PASSWORD` + base64(`user:PAT`) — `repo` scope PAT (NOT `workflow`)
12. macOS runner hangs at `Signing X.app` without `setup_ci` (no GUI keychain prompt is reachable)
13. Xcode 26 stricter Swift: `cos`/`sin` need `Foundation.` prefix; `.map { }` needs explicit `_ in` even when arg unused; `ContentUnavailableView` is iOS 17+
14. PBXFileSystemSynchronizedRootGroup auto-includes `Info.plist` → "duplicate output" — add `PBXFileSystemSynchronizedBuildFileExceptionSet`
15. Submit's 409 "cannot be reviewed" stuffs every missing field into `meta.associatedErrors` — print them to the operator

### Cross-cutting infrastructure (8 lessons)
1. GitHub PAT for git push needs `repo` only; for editing `.github/workflows/*` needs `workflow` too
2. Each iOS app needs `appPriceSchedule` even if free (USA territory + USA $0 price point)
3. The same long description works on both stores (and reused across all five apps' Android folders even when iOS-only)
4. Tablet screenshots: render at 1290×2796 (iPhone 6.7") + 2048×2732 (iPad 12.9") using the same per-app screen builders
5. Apple's chunked screenshot upload: reserve POST → PUT presigned URL with `requestHeaders` → PATCH `uploaded=true` with MD5
6. `versionCode` (Android) and `CFBundleVersion` (iOS) must be unique-per-upload; auto-increment is mandatory in CI
7. Privacy policies hosted as static HTML on GitHub Pages (separate public repo `qizhangumich/app-privacy`) work fine for both stores
8. Apple validates phone numbers — use real-format Singapore number `+65 8436 6966` (not `+0000…`)

---

## 9. How this scales

The same workspace folder, same YAML config, same scripts work for app
#1 and app #100. Marginal cost per added app:

| Resource | Marginal cost |
|----------|--------------|
| Repository size | +1 folder (~few MB after assets) |
| Lines of new code in scripts | **0** |
| Lines of new config | ~30 (1 entry per script's APPS list, 1 entry in 2 YAMLs) |
| Human time (per new app, one-time) | ~11 min |
| Human time per re-release of an existing app | **0** |
| Cloud cost (GitHub Actions free tier) | ~3 min macOS runner per iOS build, $0 |
| API quota cost (Apple/Google) | well within free quotas |

So 100 apps a year is one new spec every ~4 days. The bottleneck is
Layer 1 (brain decisions) and Layer 2 (Claude Code writing the source) —
not delivery. **Delivery is solved.**

---

## 10. What's next (the methodology will get sharper here)

The factory is shipping. The intelligence around it isn't yet hot. The
remaining work is in **Layer 1 brain** modules, which were drafted but
not yet wired to live data:

| Module | What it does | Status |
|--------|--------------|--------|
| `revenue_tracker.py` | Pulls daily downloads + revenue from Google Play + App Store Connect reports | drafted, not yet pulling live data |
| `app_scorer.py` | Re-scores backlog ideas weekly using competitor data + our own performance | drafted, needs metric inputs |
| `kill_boost.py` | Auto-removes apps with no traction; doubles-down on winners with localization + new features | drafted, decision rules in place |
| `localization_planner.py` | Picks which language to add next based on each app's geographic revenue mix | drafted; reads revenue_tracker output |
| `pricing_optimizer.py` | A/B test pricing on Apple's StoreKit + Google Play tiered pricing | drafted; needs price-experiment infra |

Daily-ops curriculum (Day 2 of the bootcamp) is wiring these to the
live data and running them as a cron. The pipeline above is the
prerequisite they all need.

---

## 11. The one rule

> If you're about to click a button in App Store Connect or Play Console,
> stop and ask: **is this the one-time setup**, or am I about to do it
> again next week? If it's the second one, the script needs the function.
> Add the function. Then ship.

That's the methodology.
