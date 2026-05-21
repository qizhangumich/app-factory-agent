//
//  PomodoroPhase.swift
//  PomodoroFocusTimer
//
//  The three phases of the Pomodoro cycle.
//

import SwiftUI

/// A phase of the Pomodoro cycle. Raw value is the persisted `type` string
/// stored on each `Session` ("focus" / "short" / "long").
enum PomodoroPhase: String, CaseIterable, Identifiable {
    case focus
    case shortBreak = "short"
    case longBreak = "long"

    var id: String { rawValue }

    /// Localized label shown above the timer ring.
    var displayName: LocalizedStringKey {
        switch self {
        case .focus:      return "phase.focus"
        case .shortBreak: return "phase.short"
        case .longBreak:  return "phase.long"
        }
    }

    /// Plain (non-localized) name for use in notification bodies built in code.
    var notificationName: String {
        switch self {
        case .focus:      return NSLocalizedString("phase.focus.plain", comment: "")
        case .shortBreak: return NSLocalizedString("phase.short.plain", comment: "")
        case .longBreak:  return NSLocalizedString("phase.long.plain", comment: "")
        }
    }

    /// Accent color for the phase, per spec.color_scheme.
    var color: Color {
        switch self {
        case .focus:      return Color(hex: 0xFF6B6B)
        case .shortBreak: return Color(hex: 0x4ECDC4)
        case .longBreak:  return Color(hex: 0x45B7D1)
        }
    }

    /// Whether this phase counts as completed focus work for stats.
    var isFocus: Bool { self == .focus }

    /// Duration in seconds for this phase given the current settings.
    func duration(using settings: AppSettings) -> Int {
        switch self {
        case .focus:      return settings.focusMinutes * 60
        case .shortBreak: return settings.shortBreakMinutes * 60
        case .longBreak:  return settings.longBreakMinutes * 60
        }
    }
}
