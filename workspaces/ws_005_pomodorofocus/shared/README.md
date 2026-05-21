# Pomodoro Focus Timer

Pomodoro Focus Timer is a native iOS and Android productivity app that runs the
classic Pomodoro Technique (25 min focus / 5 min short break / 15 min long
break, all fully customizable), tracks daily streaks with a 90-day calendar heat
map, shows focus statistics for today / week / month / all-time, and survives
backgrounding by computing remaining time from a stored start date and
scheduling a local notification for the exact timer-end moment. It collects no
data, needs no internet, and shows no ads.

## Repository layout

| Path | Contents |
|------|----------|
| `ios/` | Xcode 16 SwiftUI project (iOS 16+), Core Data, fastlane |
| `android/` | Gradle / Kotlin / Jetpack Compose project (minSdk 26), Room, fastlane |
| `shared/` | This README, the privacy policy, and the master app icon |

## iOS build instructions

Requires macOS with **Xcode 16** or newer.

1. Open `ios/PomodoroFocusTimer.xcodeproj` in Xcode (or regenerate it from
   `ios/project.yml` with [XcodeGen](https://github.com/yonaskolb/XcodeGen):
   `cd ios && xcodegen generate`).
2. Add the app icon: export `shared/app_icon.svg` to a 1024×1024 PNG (no alpha)
   and save it as
   `ios/PomodoroFocusTimer/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png`.
3. (Optional) Add looping focus-sound assets `tick.caf`, `whitenoise.caf`,
   `rain.caf` to the app target. Without them the app stays in silent mode.
4. Select the `PomodoroFocusTimer` scheme, set your signing team, and run on a
   simulator or device.
5. To distribute: `cd ios && fastlane beta` (TestFlight) or `fastlane release`.
   Signing and App Store credentials are read from environment variables — see
   `ios/fastlane/Appfile`.

Persistence note: the Core Data model is built **programmatically in code**
(`SessionStore.swift`); there is no binary `.xcdatamodeld` to maintain.

## Android build instructions

Requires **Android Studio** (Koala / 2024.1+) or a JDK 17 + Gradle 8.7 setup.

1. The binary `gradle/wrapper/gradle-wrapper.jar` is intentionally absent — see
   `android/gradle/wrapper/NOTE.md`. Opening the project in Android Studio
   regenerates it automatically, or run
   `gradle wrapper --gradle-version 8.7` from `android/`.
2. Open the `android/` folder in Android Studio and let it sync.
3. (Optional) Add looping focus-sound assets `tick.ogg`, `whitenoise.ogg`,
   `rain.ogg` to `app/src/main/res/raw/`. Without them the app stays silent.
4. Build and run the `app` configuration on an emulator or device (API 26+).
5. To distribute: `cd android && fastlane internal` or `fastlane release`.
   The Play service-account key path and package name are read from environment
   variables — see `android/fastlane/Appfile`.

Persistence note: sessions are stored with **Room**; timer settings use
**Jetpack DataStore**.
