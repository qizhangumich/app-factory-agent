package com.appfactory.pomodorofocus

import android.app.Application
import android.content.Context
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.appfactory.pomodorofocus.audio.SoundPlayer
import com.appfactory.pomodorofocus.data.PomodoroDatabase
import com.appfactory.pomodorofocus.data.Session
import com.appfactory.pomodorofocus.data.SettingsRepository
import com.appfactory.pomodorofocus.model.PomodoroPhase
import com.appfactory.pomodorofocus.model.StatsCalculator
import com.appfactory.pomodorofocus.model.StatsSummary
import com.appfactory.pomodorofocus.model.TimerSettings
import com.appfactory.pomodorofocus.notify.TimerNotifier
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import java.util.Calendar

/** Running state of the timer. */
enum class RunState { IDLE, RUNNING, PAUSED }

/** Immutable UI state for the timer screen. */
data class TimerUiState(
    val phase: PomodoroPhase = PomodoroPhase.FOCUS,
    val runState: RunState = RunState.IDLE,
    val remainingSeconds: Int = 25 * 60,
    val phaseDurationSeconds: Int = 25 * 60,
    val completedInCycle: Int = 0,
    val cycleLength: Int = 4
) {
    /** 0f..1f elapsed fraction for the progress ring. */
    val progress: Float
        get() = if (phaseDurationSeconds <= 0) 0f
        else ((phaseDurationSeconds - remainingSeconds).toFloat() / phaseDurationSeconds)
            .coerceIn(0f, 1f)

    /** "MM:SS" label. */
    val timeText: String
        get() {
            val s = remainingSeconds.coerceAtLeast(0)
            return "%02d:%02d".format(s / 60, s % 60)
        }
}

/**
 * Owns the Pomodoro timer.
 *
 * BACKGROUND-SAFE DESIGN (per spec.technical_notes):
 *  - The single sources of truth are [phaseStartElapsed] (a wall-clock
 *    timestamp) and [phaseDurationSeconds]. Remaining time is ALWAYS
 *    recomputed as duration - (now - start), so it survives the activity
 *    being stopped, the process being killed, or the device sleeping.
 *  - A coroutine "tick" loop refreshes the UI once a second; it performs no
 *    bookkeeping that would break if it stopped running.
 *  - On start a WorkManager job ([TimerNotifier]) is scheduled for the exact
 *    end time so the user is alerted even with the app closed. It is
 *    cancelled / re-scheduled on pause / reset / skip.
 *  - Engine state is mirrored to SharedPreferences so a cold relaunch
 *    mid-phase restores a running timer.
 */
class TimerViewModel(app: Application) : AndroidViewModel(app) {

    private val db = PomodoroDatabase.get(app)
    private val sessionDao = db.sessionDao()
    private val settingsRepo = SettingsRepository(app)
    private val sound = SoundPlayer(app)
    private val prefs = app.getSharedPreferences("engine", Context.MODE_PRIVATE)

    // --- Observable settings -------------------------------------------------

    val settings: StateFlow<TimerSettings> = settingsRepo.settings
        .stateIn(viewModelScope, SharingStarted.Eagerly, TimerSettings())

    // --- Observable statistics ----------------------------------------------

    val stats: StateFlow<StatsSummary> = sessionDao.observeAll()
        .map { StatsCalculator.summarize(it) }
        .stateIn(
            viewModelScope,
            SharingStarted.WhileSubscribed(5_000),
            StatsCalculator.summarize(emptyList())
        )

    // --- Timer UI state ------------------------------------------------------

    private val _uiState = MutableStateFlow(TimerUiState())
    val uiState: StateFlow<TimerUiState> = _uiState.asStateFlow()

    // --- Real timing state (the source of truth) -----------------------------

    /** Wall-clock millis when the current phase began counting; 0 = not running. */
    private var phaseStartWall: Long = 0
    /** Full duration of the current phase, seconds. */
    private var phaseDurationSeconds: Int = 25 * 60
    /** Elapsed seconds banked before the latest resume (pause/resume support). */
    private var accumulatedElapsed: Int = 0

    private var tickJob: Job? = null

    init {
        restoreState()
        // Keep idle durations in sync when the user edits settings.
        viewModelScope.launch {
            settings.collect { s ->
                _uiState.value = _uiState.value.copy(cycleLength = s.sessionsUntilLongBreak)
                if (_uiState.value.runState == RunState.IDLE && phaseStartWall == 0L) {
                    syncIdleDuration(s)
                }
            }
        }
    }

    // --- Public controls -----------------------------------------------------

    fun onStartPause() {
        when (_uiState.value.runState) {
            RunState.IDLE -> start()
            RunState.RUNNING -> pause()
            RunState.PAUSED -> resume()
        }
    }

    /** Resets the current phase to its full duration (phase unchanged). */
    fun onReset() {
        stopTicking()
        TimerNotifier.cancelTimerEnd(getApplication())
        sound.stop()
        accumulatedElapsed = 0
        phaseStartWall = 0
        phaseDurationSeconds = settings.value.durationSeconds(_uiState.value.phase)
        _uiState.value = _uiState.value.copy(
            runState = RunState.IDLE,
            remainingSeconds = phaseDurationSeconds,
            phaseDurationSeconds = phaseDurationSeconds
        )
        persistState()
    }

    /** Skips to the next phase without recording the skipped one. */
    fun onSkip() {
        stopTicking()
        TimerNotifier.cancelTimerEnd(getApplication())
        sound.stop()
        advancePhase(recordCompletion = false)
    }

    /** Permanently deletes all recorded sessions. */
    fun onResetStats() {
        viewModelScope.launch { sessionDao.deleteAll() }
    }

    /** Called when the UI returns to the foreground — recompute from the clock. */
    fun onForeground() {
        if (_uiState.value.runState != RunState.RUNNING) return
        recomputeRemaining()
        if (_uiState.value.remainingSeconds <= 0) {
            completePhase()
        } else {
            startTicking()
            sound.resume()
        }
    }

    /** Called when the UI leaves the foreground — stop the cosmetic tick only. */
    fun onBackground() {
        stopTicking()
    }

    // --- Settings mutation ---------------------------------------------------

    fun updateSettings(transform: (TimerSettings) -> TimerSettings) {
        viewModelScope.launch { settingsRepo.update(transform) }
    }

    // --- Lifecycle helpers ---------------------------------------------------

    private fun start() {
        val s = settings.value
        phaseDurationSeconds = s.durationSeconds(_uiState.value.phase)
        accumulatedElapsed = 0
        phaseStartWall = System.currentTimeMillis()
        _uiState.value = _uiState.value.copy(
            runState = RunState.RUNNING,
            remainingSeconds = phaseDurationSeconds,
            phaseDurationSeconds = phaseDurationSeconds
        )
        scheduleEndNotification()
        sound.play(s.focusSound)
        startTicking()
        persistState()
    }

    private fun pause() {
        recomputeRemaining()
        accumulatedElapsed = phaseDurationSeconds - _uiState.value.remainingSeconds
        phaseStartWall = 0
        _uiState.value = _uiState.value.copy(runState = RunState.PAUSED)
        stopTicking()
        TimerNotifier.cancelTimerEnd(getApplication())
        sound.pause()
        persistState()
    }

    private fun resume() {
        phaseStartWall = System.currentTimeMillis()
        _uiState.value = _uiState.value.copy(runState = RunState.RUNNING)
        scheduleEndNotification()
        sound.play(settings.value.focusSound)
        startTicking()
        persistState()
    }

    /** Recomputes remaining seconds purely from the wall clock. */
    private fun recomputeRemaining() {
        val remaining = if (phaseStartWall == 0L) {
            phaseDurationSeconds - accumulatedElapsed
        } else {
            val elapsed = accumulatedElapsed +
                ((System.currentTimeMillis() - phaseStartWall) / 1000).toInt()
            phaseDurationSeconds - elapsed
        }
        _uiState.value = _uiState.value.copy(remainingSeconds = remaining.coerceAtLeast(0))
    }

    private fun completePhase() {
        stopTicking()
        sound.stop()
        advancePhase(recordCompletion = true)
    }

    /** Moves to the next phase, optionally recording the finished one. */
    private fun advancePhase(recordCompletion: Boolean) {
        val finished = _uiState.value.phase
        var completedInCycle = _uiState.value.completedInCycle
        val cycleLength = settings.value.sessionsUntilLongBreak

        if (recordCompletion) {
            recordSession(finished, phaseDurationSeconds)
            if (finished.isFocus) completedInCycle++
        }

        val next: PomodoroPhase = if (finished.isFocus) {
            if (completedInCycle >= cycleLength) PomodoroPhase.LONG_BREAK
            else PomodoroPhase.SHORT_BREAK
        } else {
            if (finished == PomodoroPhase.LONG_BREAK) completedInCycle = 0
            PomodoroPhase.FOCUS
        }

        val s = settings.value
        phaseDurationSeconds = s.durationSeconds(next)
        accumulatedElapsed = 0
        phaseStartWall = 0

        val autoStart = s.autoStartNext
        _uiState.value = _uiState.value.copy(
            phase = next,
            completedInCycle = completedInCycle,
            cycleLength = cycleLength,
            remainingSeconds = phaseDurationSeconds,
            phaseDurationSeconds = phaseDurationSeconds,
            runState = if (autoStart) RunState.RUNNING else RunState.IDLE
        )

        if (autoStart) {
            phaseStartWall = System.currentTimeMillis()
            scheduleEndNotification()
            sound.play(s.focusSound)
            startTicking()
        }
        persistState()
    }

    private fun recordSession(phase: PomodoroPhase, durationSeconds: Int) {
        val now = System.currentTimeMillis()
        val session = Session(
            date = startOfDay(now),
            type = phase.storageValue,
            durationSeconds = durationSeconds,
            completedAt = now
        )
        viewModelScope.launch { sessionDao.insert(session) }
    }

    // --- UI ticking (cosmetic only) -----------------------------------------

    private fun startTicking() {
        stopTicking()
        recomputeRemaining()
        tickJob = viewModelScope.launch {
            while (isActive) {
                recomputeRemaining()
                if (_uiState.value.remainingSeconds <= 0) {
                    completePhase()
                    break
                }
                delay(500)
            }
        }
    }

    private fun stopTicking() {
        tickJob?.cancel()
        tickJob = null
    }

    // --- Notifications -------------------------------------------------------

    private fun scheduleEndNotification() {
        if (!settings.value.notificationsEnabled) return
        val remaining = _uiState.value.remainingSeconds
        if (remaining > 0) {
            TimerNotifier.scheduleTimerEnd(
                getApplication(),
                remaining.toLong(),
                _uiState.value.phase
            )
        }
    }

    private fun syncIdleDuration(s: TimerSettings) {
        val duration = s.durationSeconds(_uiState.value.phase)
        phaseDurationSeconds = duration
        _uiState.value = _uiState.value.copy(
            remainingSeconds = duration,
            phaseDurationSeconds = duration
        )
    }

    // --- State persistence ---------------------------------------------------

    private fun persistState() {
        val s = _uiState.value
        prefs.edit()
            .putString(K_PHASE, s.phase.storageValue)
            .putInt(K_RUN_STATE, s.runState.ordinal)
            .putLong(K_PHASE_START, phaseStartWall)
            .putInt(K_PHASE_DURATION, phaseDurationSeconds)
            .putInt(K_ACCUMULATED, accumulatedElapsed)
            .putInt(K_COMPLETED, s.completedInCycle)
            .apply()
    }

    private fun restoreState() {
        val phase = PomodoroPhase.fromStorage(
            prefs.getString(K_PHASE, PomodoroPhase.FOCUS.storageValue)!!
        )
        phaseDurationSeconds = prefs.getInt(K_PHASE_DURATION, 25 * 60)
        accumulatedElapsed = prefs.getInt(K_ACCUMULATED, 0)
        phaseStartWall = prefs.getLong(K_PHASE_START, 0)
        val completed = prefs.getInt(K_COMPLETED, 0)
        val savedRun = prefs.getInt(K_RUN_STATE, RunState.IDLE.ordinal)

        _uiState.value = TimerUiState(
            phase = phase,
            completedInCycle = completed,
            phaseDurationSeconds = phaseDurationSeconds,
            remainingSeconds = phaseDurationSeconds
        )

        when (savedRun) {
            RunState.RUNNING.ordinal -> {
                _uiState.value = _uiState.value.copy(runState = RunState.RUNNING)
                recomputeRemaining()
                if (_uiState.value.remainingSeconds <= 0) {
                    // Phase finished while the app was dead — advance silently.
                    advancePhase(recordCompletion = true)
                } else {
                    startTicking()
                }
            }
            RunState.PAUSED.ordinal -> {
                phaseStartWall = 0
                _uiState.value = _uiState.value.copy(
                    runState = RunState.PAUSED,
                    remainingSeconds = (phaseDurationSeconds - accumulatedElapsed)
                        .coerceAtLeast(0)
                )
            }
            else -> {
                _uiState.value = _uiState.value.copy(runState = RunState.IDLE)
            }
        }
    }

    private fun startOfDay(millis: Long): Long {
        val cal = Calendar.getInstance()
        cal.timeInMillis = millis
        cal.set(Calendar.HOUR_OF_DAY, 0)
        cal.set(Calendar.MINUTE, 0)
        cal.set(Calendar.SECOND, 0)
        cal.set(Calendar.MILLISECOND, 0)
        return cal.timeInMillis
    }

    override fun onCleared() {
        super.onCleared()
        stopTicking()
        sound.stop()
    }

    private companion object {
        const val K_PHASE = "phase"
        const val K_RUN_STATE = "runState"
        const val K_PHASE_START = "phaseStart"
        const val K_PHASE_DURATION = "phaseDuration"
        const val K_ACCUMULATED = "accumulated"
        const val K_COMPLETED = "completedInCycle"
    }
}
