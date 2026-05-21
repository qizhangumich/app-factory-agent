# Shipping Guide — Taking the 5 Apps Live

A task-oriented walkthrough: from the code-complete workspaces to apps live on
the stores. iOS builds on GitHub's macOS runners (no Mac needed); Android
builds locally in Android Studio.

| | Apps | Build where | Store account |
|---|---|---|---|
| iOS | all 5 | GitHub Actions (cloud macOS) | Apple Developer — $99/year |
| Android | ws_001, 002, 004, 005 | Android Studio (local) | Google Play — $25 once |

ws_003 (Sound Level Meter) is iOS-only by design.

---

# Part A — iOS (all 5 apps)

## A1. Enrol in the Apple Developer Program

[developer.apple.com/programs/enrol](https://developer.apple.com/programs/enrol) —
$99/year. You need an Apple ID with two-factor auth and either personal or
company identity details. Approval is usually same-day, occasionally 24-48h.
When approved you can sign in to [App Store Connect](https://appstoreconnect.apple.com).

## A2. Create an App Store Connect API key

This lets the GitHub runner authenticate without 2FA.

1. App Store Connect → **Users and Access** → **Integrations** tab → **App Store
   Connect API** → **+** → role **App Manager**.
2. **Download the `AuthKey_XXXXXXXXXX.p8`** — you only get one chance.
3. Note the **Key ID** and **Issuer ID** shown on that page.
4. Note your **Team ID**: [developer.apple.com/account](https://developer.apple.com/account)
   → Membership details (10 characters).

You now have four values: Key ID, Issuer ID, the `.p8` file, Team ID.

## A3. Register the five bundle IDs

The apps currently use the placeholder prefix `com.appfactory.*`. Using a
reverse-domain you control is best practice — see "Bundle ID prefix" below.

Apple Developer → **Certificates, IDs & Profiles** → **Identifiers** → **+** →
**App IDs** → **App**. Register one per app:

| App | Bundle ID |
|---|---|
| Tip Calculator Deluxe | com.appfactory.tipcalcdeluxe |
| Unit Converter Pro | com.appfactory.unitconverterpro |
| Sound Level Meter | com.appfactory.soundlevelmeter |
| QR & Barcode Scanner+ | com.appfactory.qrbarcodescanner |
| Pomodoro Focus Timer | com.appfactory.pomodorofocus |

Capabilities: leave defaults — none of these apps need special entitlements.

## A4. Create the five app records

App Store Connect → **Apps** → **+** → **New App**, once per app:
platform **iOS**, the app name, primary language, the matching bundle ID, and
any unique SKU (e.g. the slug). `fastlane deliver` uploads builds and metadata
into an app record that must already exist.

## A5. Push the repo to GitHub

A local git repo with two commits is already prepared. From
`D:\personal\ai_projects\3.app_factory_agent`:

```powershell
gh repo create app-factory --private --source . --remote origin --push
# …or, after creating the repo in the web UI:
git remote add origin https://github.com/<you>/app-factory.git
git push -u origin main
```

`.gitignore` already keeps every secret and build artifact out of the push.

## A6. Add the four GitHub secrets

Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository
secret**:

| Secret | Value |
|---|---|
| `ASC_KEY_ID` | Key ID from A2 |
| `ASC_ISSUER_ID` | Issuer ID from A2 |
| `ASC_KEY_P8_BASE64` | the `.p8`, base64-encoded (command below) |
| `APPLE_TEAM_ID` | Team ID from A2 |

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$HOME\Downloads\AuthKey_XXXXXXXXXX.p8")) | Set-Clipboard
```

## A7. Run the build workflow — once per app

Repo → **Actions** → **iOS Build & Upload** → **Run workflow** → pick a
workspace → **Run workflow**. Repeat for all five. Each run (~10-15 min):
checks out the repo, builds and signs the `.ipa` with automatic signing,
uploads the build + metadata to App Store Connect, and attaches the `.ipa` as
a downloadable artifact. The upload is **not** auto-submitted.

## A8. Finish each listing in App Store Connect

`deliver` uploads the title, subtitle, description and keywords. Before the
**Submit** button unlocks you must still add, per app:

- **Screenshots** — required. At minimum one 6.7" iPhone screenshot. The
  workspaces ship no screenshots yet (see "Known gaps").
- **App privacy** — choose **Data Not Collected** (true for all 5 apps).
- **Privacy policy URL** — host `shared/privacy_policy.html` publicly (see
  "Known gaps") and paste the URL.
- **Price** — Tip Calculator / Unit Converter / QR Scanner $0.99;
  Sound Level Meter / Pomodoro $1.99.
- **Age rating, category, support URL, copyright** — fill the remaining
  required fields; categories are Utilities (Productivity for Pomodoro).

## A9. Submit for review

Select the uploaded build on the app's version page → **Submit for Review**.
Apple review is typically 1-3 days. On approval the app goes live (or waits
for your manual release). This click is the "5% human gate".

---

# Part B — Android (ws_001, 002, 004, 005)

## B1. Build in Android Studio

1. **Open** → select the app's `android` folder, e.g.
   `workspaces\ws_001_tipcalcdeluxe\android`.
2. Let Gradle sync. On first sync Android Studio fetches the Gradle wrapper
   jar, SDK 35, build-tools and all dependencies — accept any install prompts.
3. Test it: **Run** on an emulator or a USB-connected device.

## B2. Create a signing keystore and a release bundle

**Build** → **Generate Signed App Bundle / APK** → **Android App Bundle** →
**Create new…** keystore (keep the keystore file and passwords safe — you
reuse one keystore across updates). Build a **release** `.aab`.

## B3. Publish to Google Play

[play.google.com/console](https://play.google.com/console) — $25 one-time.
Create the app, upload the `.aab`, complete the store listing (description,
screenshots, content rating, data-safety form → no data collected), set the
price, and roll out to production.

Repeat for the other three Android apps.

---

# Known gaps you will hit

1. **Screenshots.** Both stores require them and the workspaces ship none.
   Options: run each app in a simulator/emulator and capture manually; use a
   screenshot mockup tool; or have `fastlane snapshot` (iOS) / `screengrab`
   (Android) generate them — that needs small UI-test targets added to each
   app. Ask and this can be automated into the factory.
2. **Privacy policy URL.** Each `shared/privacy_policy.html` must be reachable
   at a public URL. Easiest: enable **GitHub Pages** on the repo and link to
   the file, or drop it on any static host.
3. **Bundle ID prefix.** `com.appfactory.*` is a placeholder. Reverse-domains
   should be one you own (e.g. `com.<yourname>.tipcalcdeluxe`). Changing it
   touches `spec.json`, `workspace.json`, the iOS `project.pbxproj` + `Appfile`
   and the Android `applicationId` — ask and all five can be rebranded
   consistently in one pass.
4. **Encryption declaration.** These apps use no non-exempt encryption. Add
   `ITSAppUsesNonExemptEncryption = false` to each iOS `Info.plist` to skip
   the per-upload export-compliance question.

# Per-app reference

| Workspace | App | iOS bundle ID | Price | Android |
|---|---|---|---|---|
| ws_001 | Tip Calculator Deluxe | com.appfactory.tipcalcdeluxe | $0.99 | yes |
| ws_002 | Unit Converter Pro | com.appfactory.unitconverterpro | $0.99 | yes |
| ws_003 | Sound Level Meter | com.appfactory.soundlevelmeter | $1.99 | — |
| ws_004 | QR & Barcode Scanner+ | com.appfactory.qrbarcodescanner | $0.99 | yes |
| ws_005 | Pomodoro Focus Timer | com.appfactory.pomodorofocus | $1.99 | yes |

Related: [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) (CI detail),
[OPERATIONS.md](OPERATIONS.md) (factory runbook).
