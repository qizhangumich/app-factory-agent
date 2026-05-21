# Unit Converter Pro — ProGuard / R8 rules.
# The app has no reflection-based code, so defaults are mostly sufficient.

# Keep Compose runtime metadata.
-keep class androidx.compose.runtime.** { *; }

# Keep data/model classes used by Kotlin serialization-free persistence.
-keep class com.appfactory.unitconverterpro.model.** { *; }

# Standard Android keep rules.
-keepattributes *Annotation*
-keepattributes SourceFile,LineNumberTable

# Suppress notes about missing optional classes.
-dontwarn org.jetbrains.annotations.**
