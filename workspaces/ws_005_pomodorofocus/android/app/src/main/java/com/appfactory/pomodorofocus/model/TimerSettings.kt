package com.appfactory.pomodorofocus.model

/**
 * Immutable snapshot of every user-configurable timer parameter.
 * Persisted via [com.appfactory.pomodorofocus.data.SettingsRepository] (DataStore).
 */
data class TimerSettings(
    val focusMinutes: Int = 25,
    val shortBreakMinutes: Int = 5,
    val longBreakMinutes: Int = 15,
    val sessionsUntilLongBreak: Int = 4,
    val autoStartNext: Boolean = false,
    val focusSound: FocusSound = FocusSound.SILENT,
    val notificationsEnabled: Boolean = true,
    val trueBlackMode: Boolean = false
) {
    /** Duration in seconds for [phase] given these settings. */
    fun durationSeconds(phase: PomodoroPhase): Int = when (phase) {
        PomodoroPhase.FOCUS -> focusMinutes * 60
        PomodoroPhase.SHORT_BREAK -> shortBreakMinutes * 60
        PomodoroPhase.LONG_BREAK -> longBreakMinutes * 60
    }

    companion object {
        // Allowed stepper ranges (spec.features).
        val FOCUS_RANGE = 1..60
        val SHORT_BREAK_RANGE = 1..30
        val LONG_BREAK_RANGE = 1..60
        val CYCLE_RANGE = 1..10
    }
}
