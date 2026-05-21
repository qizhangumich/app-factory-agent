//
//  AppSettings.swift
//  PomodoroFocusTimer
//
//  User-configurable timer parameters, persisted in UserDefaults.
//

import SwiftUI
import Combine

/// Optional focus sound played during a phase.
enum FocusSound: String, CaseIterable, Identifiable {
    case silent
    case tick
    case whiteNoise
    case rain

    var id: String { rawValue }

    var displayName: LocalizedStringKey {
        switch self {
        case .silent:     return "sound.silent"
        case .tick:       return "sound.tick"
        case .whiteNoise: return "sound.whiteNoise"
        case .rain:       return "sound.rain"
        }
    }
}

/// All persistent user preferences. Each property writes through to
/// `UserDefaults` so settings survive relaunch.
final class AppSettings: ObservableObject {

    private enum Key {
        static let focus = "focusMinutes"
        static let shortBreak = "shortBreakMinutes"
        static let longBreak = "longBreakMinutes"
        static let cycle = "sessionsUntilLongBreak"
        static let autoStart = "autoStartNext"
        static let sound = "focusSound"
        static let notifications = "notificationsEnabled"
        static let trueBlack = "trueBlackMode"
    }

    private let defaults: UserDefaults

    @Published var focusMinutes: Int {
        didSet { defaults.set(focusMinutes, forKey: Key.focus) }
    }
    @Published var shortBreakMinutes: Int {
        didSet { defaults.set(shortBreakMinutes, forKey: Key.shortBreak) }
    }
    @Published var longBreakMinutes: Int {
        didSet { defaults.set(longBreakMinutes, forKey: Key.longBreak) }
    }
    @Published var sessionsUntilLongBreak: Int {
        didSet { defaults.set(sessionsUntilLongBreak, forKey: Key.cycle) }
    }
    @Published var autoStartNext: Bool {
        didSet { defaults.set(autoStartNext, forKey: Key.autoStart) }
    }
    @Published var focusSound: FocusSound {
        didSet { defaults.set(focusSound.rawValue, forKey: Key.sound) }
    }
    @Published var notificationsEnabled: Bool {
        didSet { defaults.set(notificationsEnabled, forKey: Key.notifications) }
    }
    @Published var trueBlackMode: Bool {
        didSet { defaults.set(trueBlackMode, forKey: Key.trueBlack) }
    }

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
        // Register spec defaults so first launch matches the classic technique.
        defaults.register(defaults: [
            Key.focus: 25,
            Key.shortBreak: 5,
            Key.longBreak: 15,
            Key.cycle: 4,
            Key.autoStart: false,
            Key.sound: FocusSound.silent.rawValue,
            Key.notifications: true,
            Key.trueBlack: false
        ])
        focusMinutes = defaults.integer(forKey: Key.focus)
        shortBreakMinutes = defaults.integer(forKey: Key.shortBreak)
        longBreakMinutes = defaults.integer(forKey: Key.longBreak)
        sessionsUntilLongBreak = defaults.integer(forKey: Key.cycle)
        autoStartNext = defaults.bool(forKey: Key.autoStart)
        focusSound = FocusSound(rawValue: defaults.string(forKey: Key.sound) ?? "")
            ?? .silent
        notificationsEnabled = defaults.bool(forKey: Key.notifications)
        trueBlackMode = defaults.bool(forKey: Key.trueBlack)
    }

    // Allowed stepper ranges (spec.features).
    let focusRange = 1...60
    let shortBreakRange = 1...30
    let longBreakRange = 1...60
    let cycleRange = 1...10
}
