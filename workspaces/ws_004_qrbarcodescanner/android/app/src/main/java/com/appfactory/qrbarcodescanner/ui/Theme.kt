package com.appfactory.qrbarcodescanner.ui

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

/** Brand colors (match the spec color_scheme). */
val PrimaryBlue = Color(0xFF0A84FF)
val PrimaryBlueDark = Color(0xFF0040A8)
val ScanSuccess = Color(0xFF34C759)

/**
 * Dark-only Material 3 color scheme. The app is always dark per spec
 * (the camera feed is dark by nature).
 */
private val AppDarkColors = darkColorScheme(
    primary = PrimaryBlue,
    onPrimary = Color.White,
    primaryContainer = PrimaryBlueDark,
    onPrimaryContainer = Color.White,
    secondary = ScanSuccess,
    onSecondary = Color.White,
    background = Color(0xFF000000),
    onBackground = Color(0xFFF2F2F7),
    surface = Color(0xFF1C1C1E),
    onSurface = Color(0xFFF2F2F7),
    surfaceVariant = Color(0xFF2C2C2E),
    onSurfaceVariant = Color(0xFFAEAEB2),
    error = Color(0xFFFF453A),
)

/** Applies the app's dark Material 3 theme. */
@Composable
fun QRScannerTheme(content: @Composable () -> Unit) {
    // Always dark; isSystemInDarkTheme referenced to silence unused warnings
    // where a future light variant could plug in.
    @Suppress("UNUSED_VARIABLE")
    val systemDark = isSystemInDarkTheme()
    MaterialTheme(
        colorScheme = AppDarkColors,
        content = content,
    )
}
