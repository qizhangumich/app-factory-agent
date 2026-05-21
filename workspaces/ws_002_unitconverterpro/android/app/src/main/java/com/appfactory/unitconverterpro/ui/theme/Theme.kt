package com.appfactory.unitconverterpro.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// Indigo primary, orange accent — matches the spec color scheme.
private val IndigoPrimary = Color(0xFF4F46E5)
private val IndigoDark = Color(0xFF3730A3)
private val OrangeAccent = Color(0xFFF97316)

private val LightColors = lightColorScheme(
    primary = IndigoPrimary,
    onPrimary = Color.White,
    primaryContainer = Color(0xFFE0E7FF),
    onPrimaryContainer = IndigoDark,
    secondary = OrangeAccent,
    onSecondary = Color.White,
    tertiary = OrangeAccent,
    background = Color(0xFFF7F7FB),
    surface = Color.White,
    surfaceVariant = Color(0xFFEDEDF3)
)

private val DarkColors = darkColorScheme(
    primary = Color(0xFF9DA5FF),
    onPrimary = Color(0xFF1A1A2E),
    primaryContainer = IndigoDark,
    onPrimaryContainer = Color(0xFFE0E7FF),
    secondary = Color(0xFFFFB066),
    onSecondary = Color(0xFF3A1E00),
    tertiary = Color(0xFFFFB066),
    background = Color(0xFF121218),
    surface = Color(0xFF1C1C26),
    surfaceVariant = Color(0xFF2A2A38)
)

/** App-wide Material 3 theme with full dark mode support. */
@Composable
fun UnitConverterProTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colors = if (darkTheme) DarkColors else LightColors
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colors.background.toArgb()
            WindowCompat.getInsetsController(window, view)
                .isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colors,
        typography = Typography(),
        content = content
    )
}
