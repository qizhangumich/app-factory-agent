# Tip Calculator Deluxe

Tip Calculator Deluxe is a fast, ad-free bill-splitting utility for iOS and Android: enter a bill, set a tip percentage with a 0-50% slider, optionally add tax, choose 1-20 people (equal or unequal splits), round the total up or down, and instantly see a per-person breakdown of tip, tax and total. It works fully offline, supports dark mode and haptics, auto-detects the currency symbol from the device locale, and keeps a local history of your last 20 calculations.

## iOS build

Requires macOS with Xcode 16 (iOS 16.0+ deployment target).

1. Open `ios/TipCalculatorDeluxe.xcodeproj` in Xcode (or regenerate it with `xcodegen` using `ios/project.yml`).
2. Add a 1024x1024 PNG named `AppIcon.png` to `Assets.xcassets/AppIcon.appiconset/` (rasterize `shared/app_icon.svg`).
3. Select the `TipCalculatorDeluxe` scheme and build/run, or archive for the App Store.
4. Fastlane metadata lives in `ios/fastlane/`; set the `*_IOS_001` environment variables before running `fastlane`.

## Android build

Requires Android Studio (or Gradle 8.7) with JDK 17. Min SDK 26, target/compile SDK 35.

1. Open the `android/` folder in Android Studio. On first sync it downloads the missing `gradle/wrapper/gradle-wrapper.jar` automatically (see `gradle/wrapper/NOTE.md`).
2. Build with `./gradlew assembleRelease` or run the `app` configuration.
3. Fastlane metadata lives in `android/fastlane/`; set the `*_ANDROID_001` environment variables before running `fastlane`.
