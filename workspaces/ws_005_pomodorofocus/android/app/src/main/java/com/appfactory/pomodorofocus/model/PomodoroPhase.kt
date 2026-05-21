package com.appfactory.pomodorofocus.model

import androidx.compose.ui.graphics.Color

/**
 * The three phases of the Pomodoro cycle.
 *
 * [storageValue] is the string persisted on each [com.appfactory.pomodorofocus.data.Session].
 */
enum class PomodoroPhase(val storageValue: String) {
    FOCUS("focus"),
    SHORT_BREAK("short"),
    LONG_BREAK("long");

    /** Whether this phase counts as completed focus work for statistics. */
    val isFocus: Boolean get() = this == FOCUS

    /** Accent color for the phase, per spec.color_scheme. */
    val color: Color
        get() = when (this) {
            FOCUS -> Color(0xFFFF6B6B)
            SHORT_BREAK -> Color(0xFF4ECDC4)
            LONG_BREAK -> Color(0xFF45B7D1)
        }

    companion object {
        /** Resolves a stored string back to a phase, defaulting to FOCUS. */
        fun fromStorage(value: String): PomodoroPhase =
            entries.firstOrNull { it.storageValue == value } ?: FOCUS
    }
}
