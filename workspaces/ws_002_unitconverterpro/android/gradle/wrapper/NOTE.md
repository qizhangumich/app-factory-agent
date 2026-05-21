# gradle-wrapper.jar is intentionally not included

`gradle-wrapper.jar` is a small binary file that cannot be generated as text.
It is required for `./gradlew` to work but is absent from this source tree.

To restore it, do **one** of the following:

1. **Open the project in Android Studio.** On the first Gradle sync, Android
   Studio downloads and places the correct `gradle-wrapper.jar` automatically.

2. **Run Gradle directly** (if Gradle 8.7 is installed on the machine):

   ```
   gradle wrapper --gradle-version 8.7
   ```

   This regenerates `gradle/wrapper/gradle-wrapper.jar` plus the `gradlew`
   scripts to match.

The `gradle-wrapper.properties` file in this folder already pins Gradle 8.7,
so the wrapper will use the correct distribution once the jar is present.
