# Pomodoro Focus Timer — ProGuard / R8 rules.

# Keep line numbers for readable crash reports; hide the source file name.
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile

# --- Room ---------------------------------------------------------------
# Room generates implementations at compile time; keep the entities and DAOs.
-keep class androidx.room.** { *; }
-keep @androidx.room.Entity class * { *; }
-keep @androidx.room.Dao class * { *; }
-keep @androidx.room.Database class * { *; }
-dontwarn androidx.room.paging.**

# --- App data classes ---------------------------------------------------
# Room entity must keep its fields for the generated code.
-keep class com.appfactory.pomodorofocus.data.** { *; }

# --- WorkManager --------------------------------------------------------
-keep class * extends androidx.work.Worker
-keep class * extends androidx.work.ListenableWorker {
    public <init>(android.content.Context, androidx.work.WorkerParameters);
}

# --- Kotlin / Coroutines ------------------------------------------------
-dontwarn kotlinx.coroutines.**
-keepclassmembers class kotlin.Metadata { *; }

# --- Compose ------------------------------------------------------------
# Compose is R8-friendly; no extra rules required.
