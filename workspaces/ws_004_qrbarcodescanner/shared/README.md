# QR & Barcode Scanner+

QR & Barcode Scanner+ is an ad-free, privacy-first QR code and barcode scanner for iOS and Android. Point the camera and get an instant result; the app auto-detects whether the content is a link, Wi-Fi config, contact card, phone number, email, or plain text and offers one-tap open/copy/share. It supports QR plus EAN-13/8, UPC-A/E, Code 128, Code 39, ITF, PDF417, Aztec, and Data Matrix, keeps a private on-device history of the last 200 scans (searchable, swipe-to-delete), includes a flashlight for dark conditions, and can scan a code from an image in the photo library. There are no ads, no tracking, and no data collection of any kind — all scanning runs entirely on-device.

## iOS build instructions

- Requirements: macOS with Xcode 16 or later; iOS 16.0+ deployment target.
- The project uses one `PBXFileSystemSynchronizedRootGroup`, so new source files are picked up automatically.
- Open `ios/QRBarcodeScanner.xcodeproj` in Xcode (or regenerate it with [XcodeGen](https://github.com/yonyz/XcodeGen): `cd ios && xcodegen generate`).
- Select the `QRBarcodeScanner` scheme, set your signing team, and build/run on a physical device (the camera is unavailable in the Simulator).
- Scanning uses `AVCaptureSession` + `AVCaptureMetadataOutput`; no third-party dependencies.
- App Store delivery uses `ios/fastlane` (account `ios_001`); credentials are read from environment variables.

## Android build instructions

- Requirements: Android Studio (Koala/2024.1+) or JDK 17 + Gradle 8.7; min SDK 26, compile/target SDK 35.
- **Before first build**, supply the Gradle wrapper JAR: open the project in Android Studio (it regenerates `gradle/wrapper/gradle-wrapper.jar` automatically), or run `gradle wrapper --gradle-version 8.7` from a machine with Gradle installed. See `android/gradle/wrapper/NOTE.md`.
- Open the `android/` folder in Android Studio and let it sync, or run `./gradlew :app:assembleRelease`.
- Scanning uses Google ML Kit Barcode Scanning (bundled, fully offline) with a CameraX preview/analysis pipeline — the only non-AndroidX dependency.
- Google Play delivery uses `android/fastlane` (account `android_001`); credentials are read from environment variables.

## Shared assets

- `shared/app_icon.svg` — 1024×1024 master app icon.
- `shared/privacy_policy.html` — self-contained privacy policy for store listings.
