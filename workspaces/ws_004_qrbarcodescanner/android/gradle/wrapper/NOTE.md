# gradle-wrapper.jar is intentionally missing

This `gradle/wrapper/` directory should also contain a binary
`gradle-wrapper.jar`. Binary files cannot be authored in this environment.

To complete the wrapper, do **one** of the following on the build machine:

1. **Open the project in Android Studio.** Android Studio detects the missing
   wrapper JAR and regenerates it automatically on first sync.

2. **Run from a machine that already has Gradle 8.7 installed:**

   ```bash
   cd android
   gradle wrapper --gradle-version 8.7 --distribution-type bin
   ```

   This writes `gradle-wrapper.jar` matching `gradle-wrapper.properties`.

After the JAR is present, `./gradlew` (macOS/Linux) and `gradlew.bat`
(Windows) will work normally.
