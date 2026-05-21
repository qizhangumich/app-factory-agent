package com.appfactory.pomodorofocus.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

/** Pomodoro brand colors. */
val PomodoroRed = Color(0xFFFF6B6B)
val BreakTeal = Color(0xFF4ECDC4)
val LongBreakBlue = Color(0xFF45B7D1)
val HeatGreen = Color(0xFF4FBF4F)

private val DarkColors = darkColorScheme(
    primary = PomodoroRed,
    secondary = BreakTeal,
    tertiary = LongBreakBlue,
    background = Color(0xFF161212),
    surface = Color(0xFF1E1A1A),
    onPrimary = Color.White,
    onBackground = Color(0xFFF2EEEE),
    onSurface = Color(0xFFF2EEEE)
)

/** Variant of [DarkColors] using a pure-black background for OLED screens. */
private val TrueBlackColors = DarkColors.copy(
    background = Color.Black,
    surface = Color(0xFF0C0C0C)
)

private val LightColors = lightColorScheme(
    primary = PomodoroRed,
    secondary = BreakTeal,
    tertiary = LongBreakBlue
)

/**
 * App theme. The app is dark-first; [trueBlack] swaps in a pure-black
 * palette to save battery on OLED displays.
 */
@Composable
fun PomodoroTheme(
    trueBlack: Boolean = false,
    content: @Composable () -> Unit
) {
    // The app forces dark mode; light colors exist only as a safety fallback.
    val useDark = true || isSystemInDarkTheme()
    val colors = when {
        !useDark -> LightColors
        trueBlack -> TrueBlackColors
        else -> DarkColors
    }
    MaterialTheme(
        colorScheme = colors,
        typography = PomodoroTypography,
        content = content
    )
}
