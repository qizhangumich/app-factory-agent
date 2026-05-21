//
//  Session.swift
//  PomodoroFocusTimer
//
//  Plain value type mirroring the Core Data `SessionEntity`.
//  Data model: Session(id, date, type, durationSeconds, completedAt).
//

import Foundation

/// A completed (or in-progress, when used transiently) Pomodoro session.
struct Session: Identifiable, Hashable {
    let id: UUID
    /// Calendar day the session belongs to (start-of-day, used for grouping).
    let date: Date
    /// Phase type: focus / short / long.
    let type: PomodoroPhase
    /// Configured duration of the session in seconds.
    let durationSeconds: Int
    /// Exact timestamp the session finished.
    let completedAt: Date

    init(id: UUID = UUID(),
         date: Date,
         type: PomodoroPhase,
         durationSeconds: Int,
         completedAt: Date) {
        self.id = id
        self.date = date
        self.type = type
        self.durationSeconds = durationSeconds
        self.completedAt = completedAt
    }

    /// Whole minutes of the session (rounded down).
    var minutes: Int { durationSeconds / 60 }
}
