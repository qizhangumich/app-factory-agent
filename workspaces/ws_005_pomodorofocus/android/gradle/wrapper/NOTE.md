# gradle-wrapper.jar is intentionally missing

This repository does **not** include the binary `gradle/wrapper/gradle-wrapper.jar`
file, because binary blobs cannot be authored as text.

## How to add it

Pick whichever is easiest:

1. **Android Studio** — open this project. Android Studio detects the missing
   wrapper jar and regenerates it automatically on first sync.

2. **Command line** — if you have any Gradle 8.7 installation available:
   ```
   gradle wrapper --gradle-version 8.7 --distribution-type bin
   ```
   Run this from the `android/` directory. It writes the correct
   `gradle-wrapper.jar` next to this note.

Once the jar is present, `./gradlew` (macOS/Linux) and `gradlew.bat` (Windows)
work normally. The `gradle-wrapper.properties` here already pins Gradle 8.7.
