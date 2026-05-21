# ProGuard / R8 rules for QR & Barcode Scanner+.

# Keep generic signatures and annotations (needed by Compose / reflection).
-keepattributes Signature, InnerClasses, EnclosingMethod
-keepattributes RuntimeVisibleAnnotations, AnnotationDefault

# --- Google ML Kit Barcode Scanning ---
# ML Kit loads model components reflectively; keep its public API.
-keep class com.google.mlkit.** { *; }
-keep class com.google.android.gms.internal.mlkit_vision_barcode.** { *; }
-dontwarn com.google.mlkit.**

# --- CameraX ---
-keep class androidx.camera.** { *; }
-dontwarn androidx.camera.**

# Jetpack Compose is handled by the AGP-bundled rules; nothing extra needed.

# Keep the application entry point.
-keep class com.appfactory.qrbarcodescanner.MainActivity { *; }
