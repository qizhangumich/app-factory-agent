# Android Shipping Guide (detailed)

Everything needed to take the 4 Android apps from the workspaces to live on
Google Play. This is the **local** path — built in Android Studio on your
Windows machine, no cloud runner needed.

## The 4 Android apps

| Order | Workspace | App | Package | Price | Notes |
|---|---|---|---|---|---|
| 1st | ws_001 | Tip Calculator Deluxe | com.appfactory.tipcalcdeluxe | $0.99 | simplest — start here |
| 2nd | ws_002 | Unit Converter Pro | com.appfactory.unitconverterpro | $0.99 | offline, 3 languages |
| 3rd | ws_005 | Pomodoro Focus Timer | com.appfactory.pomodorofocus | $1.99 | Room + notifications |
| 4th | ws_004 | QR & Barcode Scanner+ | com.appfactory.qrbarcodescanner | $0.99 | camera + ML Kit — test on a real phone |

ws_003 (Sound Level Meter) is iOS-only.

Do one app end-to-end first (ws_001), confirm the whole pipeline works, then
repeat for the others.

---

## Prerequisites

- **Android Studio Koala (2024.1.1) or newer** — the projects use Android
  Gradle Plugin 8.5.2; older Studio versions will refuse it. Help → About
  shows your version; Help → Check for Updates if needed.
- ~10 GB free disk for the SDK, an emulator image, and build caches.
- Android Studio bundles its own JDK 17 (JetBrains Runtime) — no separate
  Java install needed.

---

## Stage 1 — Build and run each app locally

### 1.1 Open the project

Android Studio → **File → Open** → navigate to the app's **`android`** folder,
e.g. `D:\personal\ai_projects\3.app_factory_agent\workspaces\ws_001_tipcalcdeluxe\android`
→ **OK**. Open the `android` folder itself, not the workspace root.

### 1.2 First Gradle sync

Studio starts a Gradle sync automatically. On the first sync it downloads:

- the Gradle 8.7 distribution,
- **Android SDK Platform 35** and matching build-tools — if a yellow banner
  or a dialog offers to install missing SDK packages, **accept it**,
- all app dependencies (Compose, AndroidX, plus ML Kit for ws_004).

This takes a few minutes the first time. Watch the **Build** tab at the bottom.

### 1.3 If it complains about the Gradle wrapper

Each project ships `gradlew`/`gradlew.bat` and `gradle-wrapper.properties` but
not the binary `gradle-wrapper.jar` (it cannot be stored in git as source).
Android Studio normally regenerates it on open. If sync fails citing the
wrapper, open Studio's **Terminal** (bottom toolbar) and run:

```
gradle wrapper --gradle-version 8.7
```

(Studio's terminal has Gradle on its path.) Then **File → Sync Project with
Gradle Files**.

### 1.4 Compile — expect to fix a few things

The factory generated this Kotlin without a compiler, so the first
**Build → Make Project** (Ctrl+F9) may surface compile errors. This is
normal for first build. If you hit any, send me the Build-tab output and I
will fix them — that is exactly the factory's rejection-fix loop.

### 1.5 Run it

**Device Manager** (right toolbar) → **Create Device** → pick e.g. Pixel 7,
a system image (API 35) → Finish. Then press **Run** (green triangle). Or
plug in an Android phone with **USB debugging** enabled (Settings → About →
tap Build Number 7×, then Developer Options → USB debugging) and select it.

For ws_004 (QR scanner) test on a **physical phone** — the emulator's fake
camera cannot scan real codes.

---

## Stage 2 — Build a signed release bundle

Google Play requires a signed **Android App Bundle** (`.aab`), not an APK.

### 2.1 Create an upload keystore (once — reuse for all 4 apps)

**Build → Generate Signed App Bundle / APK → Android App Bundle → Next →**
under *Key store path* click **Create new…**:

- **Key store path:** somewhere safe and **outside** the repo, e.g.
  `D:\personal\keys\appfactory-upload.jks`
- **Password:** a strong keystore password
- **Key alias:** `upload`
- **Key password:** a strong key password
- **Validity:** 30+ years
- **Certificate:** fill name / organisation (any real values)

You can reuse this one keystore + `upload` alias for all four apps.

### 2.2 Build the bundle

Back in the wizard: select the keystore, enter the passwords → **Next** →
build variant **release** → **Create**. Studio shows a notification with a
*locate* link; the file is:

```
workspaces\ws_001_tipcalcdeluxe\android\app\release\app-release.aab
```

### 2.3 Back up the keystore — critical

Copy the `.jks` file and its passwords to a password manager / secure backup.
With Play App Signing a lost upload key is recoverable, but treat it as
irreplaceable. **Never commit it** — the repo `.gitignore` already blocks
`*.keystore`/`*.jks`.

---

## Stage 3 — Publish on Google Play

### 3.1 Create a Google Play developer account

[play.google.com/console](https://play.google.com/console) — **$25 one-time**.
Google now verifies identity (and, for organisations, the D-U-N-S number);
verification can take **a few days**. Start this early.

### 3.2 ⚠️ New personal accounts: the 12-tester / 14-day rule

If your developer account is **personal** and created recently, Google
requires you to run a **closed test with at least 12 testers who stay opted
in for 14 continuous days** before you may apply for production access. Plan
for this — it adds two weeks before the first app can go public. A
**company/organisation** account is exempt. Decide which account type to
register accordingly.

### 3.3 Create the app

Play Console → **Create app**: app name, default language, **App**,
**Paid** (these are paid apps). Accept the declarations.

### 3.4 Store listing assets — what you must supply

Play needs more graphics than the App Store. Per app:

| Asset | Spec | Status |
|---|---|---|
| App icon | 512×512 PNG (32-bit, alpha OK) | **needs generating** from `shared/app_icon.svg` |
| Feature graphic | 1024×500 PNG/JPG (no alpha) | **needs creating** |
| Phone screenshots | 2-8, PNG/JPG, 16:9 or 9:16 | **needs capturing** |
| Short description | ≤80 chars | ready: `android/fastlane/metadata/android/en-US/short_description.txt` |
| Full description | ≤4000 chars | ready: `…/full_description.txt` |
| Title | ≤30 chars | ready: `…/title.txt` |

The text is done; the three image assets are the gap (see "Asset gaps").

### 3.5 Required forms

In **Policy → App content**, complete:

- **Privacy policy** — paste a public URL to the app's privacy policy
  (`shared/privacy_policy.html` must be hosted; GitHub Pages is free).
- **Data safety** — declare **No data collected / No data shared** (true for
  all factory apps).
- **Content rating** — fill the questionnaire (these are utility apps → rated
  Everyone).
- **Target audience**, **Ads** (declare *No ads*), **App access** (no login).

### 3.6 Pricing and a payments profile

Paid apps need a **payments/merchant profile**: Play Console → **Setup →
Payments profile**. Then set the price under **Monetise → Products → App
pricing** (Tip Calculator / Unit Converter / QR $0.99; Pomodoro $1.99).
Merchant registration is unavailable in a few countries — check yours.

### 3.7 Upload and roll out

**Testing → Internal testing → Create release** → upload `app-release.aab` →
add release notes → save → review → roll out to internal testing. Verify the
install from the tester link. Then promote: internal → (closed test if 3.2
applies) → **Production**.

---

## Asset gaps to close before submitting

1. **512×512 Play icon** — render from `shared/app_icon.svg` (the existing
   `render_icons.py` can be extended to emit these).
2. **1024×500 feature graphic** — a simple branded banner per app; can be
   generated.
3. **Screenshots** — capture from the running app (Studio's emulator has a
   camera-shutter button in its toolbar) or via `fastlane screengrab`.
4. **Privacy-policy hosting** — turn on GitHub Pages and link each
   `shared/privacy_policy.html`.

I can automate items 1, 2 and 4. Just ask.

---

## Optional — automate uploads with Fastlane

Once the manual flow works, `delivery/Fastfile`'s `android deploy` lane +
`.github/workflows/android_deploy.yml` can build and upload future versions
automatically. See [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md).
