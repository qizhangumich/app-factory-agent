# App Factory — Tip Calculator Deluxe ProGuard rules.
#
# The app uses only AndroidX + Jetpack Compose, which ship their own
# consumer ProGuard rules, so very little is needed here.

# Keep Compose runtime metadata intact.
-keep class androidx.compose.** { *; }
-dontwarn androidx.compose.**

# Keep the data model used for SharedPreferences (de)serialization by name.
-keep class com.appfactory.tipcalcdeluxe.model.** { *; }

# Standard Kotlin metadata.
-keepattributes *Annotation*, InnerClasses, Signature, RuntimeVisibleAnnotations
