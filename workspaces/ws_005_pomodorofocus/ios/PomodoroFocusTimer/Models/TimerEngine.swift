//
//  TimerEngine.swift
//  PomodoroFocusTimer
//
//  The heart of the app.
//
//  BACKGROUND-SAFE DESIGN (per spec.technical_notes):
//  * We NEVER rely on a Timer firing in the background — iOS suspends it.
//  * The single sources of truth are `phaseStartDate` and the running
//    phase's `duration`. Remaining time is ALWAYS computed as
//    duration - (now - phaseStartDate), so it stays correct after the app
//    is backgrounded, suspended, or relaunched.
//  * A foreground `Timer` exists only to drive the UI tick (1 Hz); it does
//    no bookkeeping that would break if it stopped firing.
//  * On start we schedule a `UNTimeIntervalNotificationTrigger` for the
//    exact end time so the user is alerted even while suspended. The
//    notification is cancelled and rescheduled on pause / reset / skip.
//  * Engine state is mirrored to UserDefaults so a cold relaunch mid-phase
//    restores the running timer.
//

import SwiftUI
import Combine
import AVFoundation

/// Running state of the timer.
enum TimerRunState {
    case idle      // stopped, never started or fully reset
    case running   // counting down
    case paused    // counting down suspended, retains remaining time
}

@MainActor
final class TimerEngine: ObservableObject {

    // MARK: - Published UI state

    /// Current phase (focus / short break / long break).
    @Published private(set) var phase: PomodoroPhase = .focus
    /// Run state.
    @Published private(set) var runState: TimerRunState = .idle
    /// Seconds remaining in the current phase (recomputed every tick).
    @Published private(set) var remainingSeconds: Int = 25 * 60
    /// Number of focus sessions completed in the CURRENT cycle (0..<cycleLength).
    @Published private(set) var completedInCycle: Int = 0
    /// Total focus sessions ever completed this run (drives the dots when > cycle).
    @Published private(set) var focusSessionsToday: Int = 0

    // MARK: - Dependencies

    private let settings: AppSettings
    private let store: SessionStore
    private let notifications = NotificationManager()
    private let sound = SoundPlayer()

    // MARK: - Timing state (the real source of truth)

    /// When the current phase began counting. Nil when idle.
    private var phaseStartDate: Date?
    /// Full duration of the current phase in seconds.
    private var phaseDuration: Int = 25 * 60
    /// Seconds already elapsed before the most recent resume (for pause/resume).
    private var accumulatedElapsed: Int = 0

    private var uiTimer: AnyCancellable?
    private var cancellables = Set<AnyCancellable>()

    // MARK: - Persistence keys for crash/relaunch restoration

    private enum K {
        static let phase = "engine.phase"
        static let runState = "engine.runState"
        static let phaseStart = "engine.phaseStart"
        static let phaseDuration = "engine.phaseDuration"
        static let accumulated = "engine.accumulatedElapsed"
        static let completedInCycle = "engine.completedInCycle"
        static let focusToday = "engine.focusSessionsToday"
        static let focusDay = "engine.focusDay"
    }

    init(settings: AppSettings, store: SessionStore) {
        self.settings = settings
        self.store = store
        restoreState()

        // If the user changes durations while idle, reflect them immediately.
        settings.objectWillChange
            .receive(on: RunLoop.main)
            .sink { [weak self] in self?.syncDurationIfIdle() }
            .store(in: &cancellables)
    }

    // MARK: - Derived values

    /// Number of dots / sessions per long-break cycle.
    var cycleLength: Int { settings.sessionsUntilLongBreak }

    /// Progress 0...1 of the current phase (for the ring).
    var progress: Double {
        guard phaseDuration > 0 else { return 0 }
        let done = Double(phaseDuration - remainingSeconds)
        return min(1, max(0, done / Double(phaseDuration)))
    }

    /// "MM:SS" string for the center label.
    var timeString: String {
        let s = max(0, remainingSeconds)
        return String(format: "%02d:%02d", s / 60, s % 60)
    }

    // MARK: - Public controls

    /// Start or resume the timer.
    func startOrPause() {
        switch runState {
        case .idle:    start()
        case .running: pause()
        case .paused:  resume()
        }
    }

    /// Reset the current phase back to its full duration (does not change phase).
    func reset() {
        stopTicking()
        notifications.cancelTimerNotification()
        sound.stop()
        accumulatedElapsed = 0
        phaseStartDate = nil
        phaseDuration = phase.duration(using: settings)
        remainingSeconds = phaseDuration
        runState = .idle
        persistState()
    }

    /// Skip to the next phase without recording the skipped one.
    func skip() {
        stopTicking()
        notifications.cancelTimerNotification()
        sound.stop()
        advancePhase(recordingCompletion: false)
    }

    /// Called from `RootView` whenever the app returns to the foreground.
    /// Recomputes remaining time and finishes the phase if it elapsed while away.
    func handleForeground() {
        guard runState == .running else { return }
        recomputeRemaining()
        if remainingSeconds <= 0 {
            completePhase()
        } else {
            startTicking()
            sound.resumeIfNeeded(settings.focusSound)
        }
    }

    /// Called when the app moves to the background — stop the UI timer only.
    func handleBackground() {
        stopTicking() // the date math + notification keep everything correct
    }

    // MARK: - Lifecycle helpers

    private func start() {
        phaseDuration = phase.duration(using: settings)
        accumulatedElapsed = 0
        phaseStartDate = Date()
        remainingSeconds = phaseDuration
        runState = .running
        scheduleEndNotification()
        sound.play(settings.focusSound)
        startTicking()
        Haptics.light()
        persistState()
    }

    private func pause() {
        recomputeRemaining()
        accumulatedElapsed = phaseDuration - remainingSeconds
        phaseStartDate = nil
        runState = .paused
        stopTicking()
        notifications.cancelTimerNotification()
        sound.pause()
        persistState()
    }

    private func resume() {
        phaseStartDate = Date()
        runState = .running
        scheduleEndNotification()
        sound.play(settings.focusSound)
        startTicking()
        persistState()
    }

    /// Recomputes `remainingSeconds` purely from dates — the background-safe core.
    private func recomputeRemaining() {
        guard let start = phaseStartDate else {
            remainingSeconds = max(0, phaseDuration - accumulatedElapsed)
            return
        }
        let elapsed = accumulatedElapsed + Int(Date().timeIntervalSince(start))
        remainingSeconds = max(0, phaseDuration - elapsed)
    }

    /// Phase finished naturally — record it and advance.
    private func completePhase() {
        stopTicking()
        sound.stop()
        Haptics.success()
        advancePhase(recordingCompletion: true)
    }

    /// Moves to the next phase in the Pomodoro cycle.
    /// - Parameter recordingCompletion: when true the just-finished phase is
    ///   stored as a `Session` for the statistics screen.
    private func advancePhase(recordingCompletion: Bool) {
        let finished = phase

        if recordingCompletion {
            store.add(type: finished, durationSeconds: phaseDuration)
            if finished.isFocus {
                completedInCycle += 1
                focusSessionsToday += 1
            }
        }

        // Decide the next phase.
        let next: PomodoroPhase
        if finished.isFocus {
            next = completedInCycle >= cycleLength ? .longBreak : .shortBreak
        } else {
            if finished == .longBreak { completedInCycle = 0 }
            next = .focus
        }

        phase = next
        phaseDuration = next.duration(using: settings)
        remainingSeconds = phaseDuration
        accumulatedElapsed = 0
        phaseStartDate = nil

        if settings.autoStartNext {
            // Chain straight into the next phase.
            phaseStartDate = Date()
            runState = .running
            scheduleEndNotification()
            sound.play(settings.focusSound)
            startTicking()
        } else {
            runState = .idle
        }
        persistState()
    }

    // MARK: - UI ticking (cosmetic only)

    private func startTicking() {
        stopTicking()
        recomputeRemaining()
        uiTimer = Timer.publish(every: 0.5, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in self?.tick() }
    }

    private func stopTicking() {
        uiTimer?.cancel()
        uiTimer = nil
    }

    private func tick() {
        recomputeRemaining()
        if remainingSeconds <= 0 {
            completePhase()
        }
    }

    // MARK: - Notifications

    private func scheduleEndNotification() {
        guard settings.notificationsEnabled, remainingSeconds > 0 else { return }
        notifications.scheduleTimerNotification(after: TimeInterval(remainingSeconds),
                                                endingPhase: phase)
    }

    // MARK: - Settings sync

    private func syncDurationIfIdle() {
        guard runState == .idle, phaseStartDate == nil else { return }
        phaseDuration = phase.duration(using: settings)
        remainingSeconds = phaseDuration
    }

    // MARK: - State persistence

    private func persistState() {
        let d = UserDefaults.standard
        d.set(phase.rawValue, forKey: K.phase)
        d.set(stateRaw(runState), forKey: K.runState)
        if let start = phaseStartDate {
            d.set(start.timeIntervalSince1970, forKey: K.phaseStart)
        } else {
            d.removeObject(forKey: K.phaseStart)
        }
        d.set(phaseDuration, forKey: K.phaseDuration)
        d.set(accumulatedElapsed, forKey: K.accumulated)
        d.set(completedInCycle, forKey: K.completedInCycle)
        d.set(focusSessionsToday, forKey: K.focusToday)
        d.set(Calendar.current.startOfDay(for: Date()).timeIntervalSince1970,
              forKey: K.focusDay)
    }

    private func restoreState() {
        let d = UserDefaults.standard
        guard d.object(forKey: K.phase) != nil else {
            // Fresh install — derive defaults from settings.
            phaseDuration = PomodoroPhase.focus.duration(using: settings)
            remainingSeconds = phaseDuration
            return
        }
        phase = PomodoroPhase(rawValue: d.string(forKey: K.phase) ?? "focus") ?? .focus
        phaseDuration = d.integer(forKey: K.phaseDuration)
        accumulatedElapsed = d.integer(forKey: K.accumulated)
        completedInCycle = d.integer(forKey: K.completedInCycle)

        // Reset the day counter if we crossed midnight.
        let savedDay = d.double(forKey: K.focusDay)
        let today = Calendar.current.startOfDay(for: Date()).timeIntervalSince1970
        focusSessionsToday = (savedDay == today) ? d.integer(forKey: K.focusToday) : 0

        let savedState = d.integer(forKey: K.runState)
        if savedState == 1, d.object(forKey: K.phaseStart) != nil {
            // Was running — restore the start date and recompute.
            phaseStartDate = Date(timeIntervalSince1970: d.double(forKey: K.phaseStart))
            runState = .running
            recomputeRemaining()
            if remainingSeconds <= 0 {
                // It finished while the app was dead — advance silently.
                advancePhase(recordingCompletion: true)
            } else {
                startTicking()
            }
        } else if savedState == 2 {
            runState = .paused
            phaseStartDate = nil
            remainingSeconds = max(0, phaseDuration - accumulatedElapsed)
        } else {
            runState = .idle
            remainingSeconds = phaseDuration > 0
                ? phaseDuration
                : PomodoroPhase.focus.duration(using: settings)
        }
    }

    private func stateRaw(_ s: TimerRunState) -> Int {
        switch s {
        case .idle: return 0
        case .running: return 1
        case .paused: return 2
        }
    }
}
