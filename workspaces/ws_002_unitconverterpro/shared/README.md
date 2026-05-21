# Unit Converter Pro

Unit Converter Pro is an offline-first measurement converter for iOS and Android. It covers 16 unit categories with NIST-correct conversion factors hardcoded into the app, real-time conversion as you type, favorite conversion pairs, a 100-entry history with timestamps, unit search, a one-tap swap button, and clipboard copy. The app collects no data, requests no permissions, and works entirely without an internet connection. It is localized in English, Japanese, and German.

## iOS build instructions

- Requires macOS with Xcode 16+ (iOS 16.0 deployment target).
- Open `ios/UnitConverterPro.xcodeproj` in Xcode, select the `UnitConverterPro` scheme, choose a simulator or device, and Build & Run.
- The project uses a `PBXFileSystemSynchronizedRootGroup`, so new `.swift` files in `UnitConverterPro/` are picked up automatically — no manual project edits needed.
- Alternatively, regenerate the project from `ios/project.yml` with [XcodeGen](https://github.com/yonaskolb/XcodeGen): `cd ios && xcodegen generate`.
- App Store metadata and Fastlane config live under `ios/fastlane/`. Add a real 1024×1024 PNG to the `AppIcon.appiconset` before submission.

## Android build instructions

- Requires Android Studio (Ladybug or newer) with Android SDK 35 and JDK 17.
- Open the `android/` folder in Android Studio. Let it sync Gradle (8.7).
- `gradle/wrapper/gradle-wrapper.jar` is a binary that is not included in source — Android Studio regenerates it on first sync, or run `gradle wrapper --gradle-version 8.7`. See `android/gradle/wrapper/NOTE.md`.
- Build & Run on an emulator or device (minSdk 26, Android 8.0+).
- Play Store metadata and Fastlane config live under `android/fastlane/`.

## Project layout

- `ios/` — SwiftUI app, Xcode project, Fastlane metadata.
- `android/` — Jetpack Compose app, Gradle build, Fastlane metadata.
- `shared/` — privacy policy, master app icon, this README.
