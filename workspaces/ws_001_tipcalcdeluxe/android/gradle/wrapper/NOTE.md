# gradle-wrapper.jar is missing on purpose

`gradle-wrapper.jar` is a small binary file that cannot be created as text in
this environment. The Gradle wrapper scripts (`gradlew`, `gradlew.bat`) and
`gradle-wrapper.properties` are present, but the `.jar` must be added before
the project will build.

## How to add it

Option A — open the project in Android Studio. Android Studio detects the
missing wrapper jar and downloads it automatically on first sync.

Option B — from a machine that already has Gradle 8.7 installed, run this in
the `android/` directory:

    gradle wrapper --gradle-version 8.7

That command regenerates `gradle/wrapper/gradle-wrapper.jar` to match the
version pinned in `gradle-wrapper.properties`.

Once `gradle-wrapper.jar` exists, `./gradlew assembleRelease` will work.
