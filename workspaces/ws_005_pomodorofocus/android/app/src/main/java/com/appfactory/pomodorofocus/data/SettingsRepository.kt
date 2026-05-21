package com.appfactory.pomodorofocus.data

import android.content.Context
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.appfactory.pomodorofocus.model.FocusSound
import com.appfactory.pomodorofocus.model.TimerSettings
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

/** Single DataStore instance scoped to the application context. */
private val Context.settingsStore by preferencesDataStore(name = "pomodoro_settings")

/**
 * Persists [TimerSettings] to Jetpack DataStore and exposes them as a [Flow].
 */
class SettingsRepository(private val context: Context) {

    private object Keys {
        val FOCUS = intPreferencesKey("focusMinutes")
        val SHORT = intPreferencesKey("shortBreakMinutes")
        val LONG = intPreferencesKey("longBreakMinutes")
        val CYCLE = intPreferencesKey("sessionsUntilLongBreak")
        val AUTO_START = booleanPreferencesKey("autoStartNext")
        val SOUND = stringPreferencesKey("focusSound")
        val NOTIFICATIONS = booleanPreferencesKey("notificationsEnabled")
        val TRUE_BLACK = booleanPreferencesKey("trueBlackMode")
    }

    /** Observes the current settings, emitting spec defaults when unset. */
    val settings: Flow<TimerSettings> = context.settingsStore.data.map { prefs ->
        val defaults = TimerSettings()
        TimerSettings(
            focusMinutes = prefs[Keys.FOCUS] ?: defaults.focusMinutes,
            shortBreakMinutes = prefs[Keys.SHORT] ?: defaults.shortBreakMinutes,
            longBreakMinutes = prefs[Keys.LONG] ?: defaults.longBreakMinutes,
            sessionsUntilLongBreak = prefs[Keys.CYCLE] ?: defaults.sessionsUntilLongBreak,
            autoStartNext = prefs[Keys.AUTO_START] ?: defaults.autoStartNext,
            focusSound = FocusSound.fromStorage(prefs[Keys.SOUND] ?: ""),
            notificationsEnabled = prefs[Keys.NOTIFICATIONS] ?: defaults.notificationsEnabled,
            trueBlackMode = prefs[Keys.TRUE_BLACK] ?: defaults.trueBlackMode
        )
    }

    suspend fun update(transform: (TimerSettings) -> TimerSettings) {
        // Read-modify-write so any single field can be changed atomically.
        context.settingsStore.edit { prefs ->
            val current = TimerSettings(
                focusMinutes = prefs[Keys.FOCUS] ?: 25,
                shortBreakMinutes = prefs[Keys.SHORT] ?: 5,
                longBreakMinutes = prefs[Keys.LONG] ?: 15,
                sessionsUntilLongBreak = prefs[Keys.CYCLE] ?: 4,
                autoStartNext = prefs[Keys.AUTO_START] ?: false,
                focusSound = FocusSound.fromStorage(prefs[Keys.SOUND] ?: ""),
                notificationsEnabled = prefs[Keys.NOTIFICATIONS] ?: true,
                trueBlackMode = prefs[Keys.TRUE_BLACK] ?: false
            )
            val next = transform(current)
            prefs[Keys.FOCUS] = next.focusMinutes
            prefs[Keys.SHORT] = next.shortBreakMinutes
            prefs[Keys.LONG] = next.longBreakMinutes
            prefs[Keys.CYCLE] = next.sessionsUntilLongBreak
            prefs[Keys.AUTO_START] = next.autoStartNext
            prefs[Keys.SOUND] = next.focusSound.storageValue
            prefs[Keys.NOTIFICATIONS] = next.notificationsEnabled
            prefs[Keys.TRUE_BLACK] = next.trueBlackMode
        }
    }
}
