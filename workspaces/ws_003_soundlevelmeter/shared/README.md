# Sound Level Meter

Sound Level Meter turns an iPhone into a real-time decibel meter. It uses the built-in microphone via `AVAudioRecorder` metering to measure ambient sound at 10 readings per second, displaying the level on an animated semicircular needle gauge with a large digital readout, min/max/average/peak statistics, color-coded safety bands, a NIOSH-based noise-exposure-time warning, a scrolling session chart, a calibration offset, and pause/resume control. The app is iOS-only, pure SwiftUI, requires no internet connection, collects no data, and records no audio.

## iOS build instructions

Requires macOS with Xcode 16 or later.

1. Open `ios/SoundLevelMeter.xcodeproj` in Xcode (or regenerate it with [XcodeGen](https://github.com/yonyz/XcodeGen): run `xcodegen generate` inside `ios/` using `project.yml`).
2. Replace the placeholder app icon: render `shared/app_icon.svg` to a 1024x1024 PNG and save it as `ios/SoundLevelMeter/Assets.xcassets/AppIcon.appiconset/AppIcon.png`.
3. Select the `SoundLevelMeter` scheme and a physical device (the microphone is not available on the Simulator).
4. Set your signing team under Signing & Capabilities (bundle id `com.appfactory.soundlevelmeter`).
5. Build and run, or archive for distribution.

### Fastlane

Metadata for the App Store lives in `ios/fastlane/metadata` (en-US, ja, de-DE). The `Appfile` reads credentials from environment variables (`SLM_APPLE_ID`, `SLM_TEAM_ID`, `SLM_ITC_TEAM_ID`, or an App Store Connect API key). Add screenshots to `ios/fastlane/metadata/screenshots` before uploading.

## Notes

iPhone microphones are not laboratory calibrated, so readings are an approximation. The dB value is derived from `averagePowerForChannel` plus a fixed offset and a user-adjustable calibration offset; it should not be used for legal, medical, or occupational compliance.
