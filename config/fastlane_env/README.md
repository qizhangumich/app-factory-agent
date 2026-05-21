# Fastlane Credentials — [HUMAN GATE]

This directory holds the secrets that let the delivery layer build, sign, and upload
apps. **None of the real files belong in version control.**

## What goes here

| File pattern | Purpose | Created by |
|---|---|---|
| `ios_XXX.env` | Apple ID, Team ID, App Store Connect API key per iOS account | Human, once |
| `android_XXX.env` | Play service-account JSON path + keystore details per Android account | Human, once |
| `AuthKey_*.p8` | App Store Connect API private keys | Downloaded from Apple |
| `play-android-XXX.json` | Google Play service-account keys | Downloaded from Google Cloud |
| `*.keystore` | Android upload keystores | Generated with `keytool` |

## Setup (one time)

1. Copy each `*.env.example` to its real name (`ios_001.env.example` → `ios_001.env`).
2. Fill in real values for all 6 iOS + 6 Android accounts.
3. Generate an App Store Connect API key per iOS account and save the `.p8` here.
4. Create a Google Play service account per Android account and save the JSON here.
5. Generate one upload keystore per Android account with `keytool`.
6. Run `fastlane match init` once to create the shared signing-cert repo.

Everything in this folder except `*.example` and this README is gitignored.
