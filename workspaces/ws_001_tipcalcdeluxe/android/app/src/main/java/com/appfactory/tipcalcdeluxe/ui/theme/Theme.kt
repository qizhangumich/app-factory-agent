package com.appfactory.tipcalcdeluxe.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// System-blue primary, system-green accent for money (spec.color_scheme).
private val BrandBlue = Color(0xFF007AFF)
private val BrandBlueDark = Color(0xFF0A84FF)
private val MoneyGreen = Color(0xFF34C759)
private val MoneyGreenDark = Color(0xFF30D158)

private val LightColors = lightColorScheme(
    primary = BrandBlue,
    onPrimary = Color.White,
    secondary = MoneyGreen,
    onSecondary = Color.White,
    tertiary = MoneyGreen
)

private val DarkColors = darkColorScheme(
    primary = BrandBlueDark,
    onPrimary = Color.White,
    secondary = MoneyGreenDark,
    onSecondary = Color.Black,
    tertiary = MoneyGreenDark
)

/** Material 3 theme with full dark-mode and dynamic-color support. */
@Composable
fun TipCalculatorDeluxeTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val context = LocalContext.current
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            if (darkTheme) dynamicDarkColorScheme(context)
            else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColors
        else -> LightColors
    }

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.background.toArgb()
            WindowCompat.getInsetsController(window, view)
                .isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography(),
        content = content
    )
}
