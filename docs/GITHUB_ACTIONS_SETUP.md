# Shipping iOS from Windows via GitHub Actions

This builds and uploads your iOS apps on GitHub's hosted macOS runners — you
never need to own or rent a Mac. The workflow is `.github/workflows/ios_deploy.yml`.

## What this does and does not remove

| Removed | Still required |
|---|---|
| Buying / renting a Mac | An Apple Developer account ($99/year, per account) |
| Installing Xcode | Creating each app record in App Store Connect |
| Local iOS build setup | App icon PNGs (see "Known gaps" below) |

The macOS *build machine* is free. The Apple *account and store setup* is the
one-time human-gate work the instruction book calls out — it cannot be skipped.

## Cost note

GitHub Actions macOS minutes bill at **10×** the normal rate. A private repo's
free tier (~2000 min/month) gives roughly **200 macOS-minutes** — about 12-18
builds. A **public repo gets unlimited free minutes**. Pick accordingly.

---

## Step 1 — Push the repo to GitHub

A local git repo with an initial commit has already been created for you. From
`D:\personal\ai_projects\3.app_factory_agent`:

```powershell
# Create the GitHub repo and push (GitHub CLI — run 'gh auth login' first):
gh repo create app-factory --private --source . --remote origin --push

# …or, if you made the repo in the GitHub web UI:
git remote add origin https://github.com/<you>/app-factory.git
git push -u origin main
```

The `.gitignore` already excludes every secret and build artifact — nothing
sensitive gets pushed.

## Step 2 — Apple-side setup (once)

1. **Apple Developer account** — enroll at developer.apple.com ($99/year).
   Enroll each of the factory's iOS accounts you intend to ship from.
2. **App Store Connect API key** — App Store Connect → *Users and Access* →
   *Integrations* → *App Store Connect API* → generate a key with the
   **App Manager** role. Download the `AuthKey_XXXXXXXXXX.p8` (one chance to
   download). Note the **Key ID** and the **Issuer ID** shown on that page.
3. **Team ID** — App Store Connect → *Membership* → copy the 10-character Team ID.
4. **Create the app record** — App Store Connect → *Apps* → **+** → *New App*.
   Set the bundle ID to match the app's `spec.json` (e.g.
   `com.appfactory.tipcalcdeluxe`), pick a name and SKU. `deliver` uploads to
   an existing app record; it will not create one.

## Step 3 — Add the GitHub secrets

Repo → *Settings* → *Secrets and variables* → *Actions* → *New repository secret*.

| Secret | Value |
|---|---|
| `ASC_KEY_ID` | the API Key ID from step 2.2 |
| `ASC_ISSUER_ID` | the Issuer ID from step 2.2 |
| `ASC_KEY_P8_BASE64` | the `.p8` file, base64-encoded (command below) |
| `APPLE_TEAM_ID` | the Team ID from step 2.3 |

Base64-encode the `.p8` on Windows PowerShell and copy it to the clipboard:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$HOME\Downloads\AuthKey_XXXXXXXXXX.p8")) | Set-Clipboard
```

Paste that as the value of `ASC_KEY_P8_BASE64`.

That is all four. The workflow uses **automatic signing** — Xcode on the runner
creates and manages the distribution certificate via the API key, so no
certificates repository is needed to get started.

## Step 4 — Run it

Repo → *Actions* tab → **iOS Build & Upload** → *Run workflow* → choose a
workspace (e.g. `ws_001_tipcalcdeluxe`) → *Run workflow*.

The runner checks out the repo, picks Xcode, builds and signs the `.ipa`, and
uploads it to App Store Connect as a build (not submitted). The `.ipa` is also
attached to the run as a downloadable artifact. Then open App Store Connect,
review the metadata, and click **Submit for Review** — the 5% human gate.

---

## Known gaps to clear before the first green build

1. **App icons — done.** All five iOS apps have a flat 1024×1024 RGB
   `AppIcon` PNG (no alpha), rendered from `shared/app_icon.svg` by
   `scripts/render_icons.py`. Re-run that script if an SVG changes.
2. **App record must exist** in App Store Connect first (step 2.4).
3. **Bundle IDs** in each `spec.json` must be registered to your team.

## Optional — fastlane match (harden later)

The default automatic signing is fine for one account. At multi-account scale,
`fastlane match` keeps one shared certificate across accounts. To switch on:
create a private "certs" repo, run `fastlane match appstore` once (this works
on Windows — it is API-driven), then add the `MATCH_GIT_URL`, `MATCH_PASSWORD`,
and `MATCH_GIT_BASIC_AUTHORIZATION` secrets. The Fastfile picks match up
automatically when `MATCH_GIT_URL` is set — no code change needed.

## Android too

`.github/workflows/android_deploy.yml` does the same on free Linux runners.
Its secrets are listed in the file header.
