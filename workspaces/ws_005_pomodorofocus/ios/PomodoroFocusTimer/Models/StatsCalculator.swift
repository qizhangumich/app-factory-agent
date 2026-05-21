//
//  StatsCalculator.swift
//  PomodoroFocusTimer
//
//  Pure functions that turn a list of `Session`s into the figures shown
//  on the Stats screen: focus minutes, streaks and the 90-day heat map.
//

import Foundation

/// Aggregated figures for one calendar day.
struct DayStats: Identifiable {
    let id: Date          // start-of-day
    let date: Date
    let focusSessions: Int
    let focusMinutes: Int
}

/// Stateless statistics engine. All inputs are explicit so it is trivial to test.
enum StatsCalculator {

    private static var calendar: Calendar {
        var c = Calendar.current
        c.firstWeekday = 2 // Monday
        return c
    }

    /// Focus sessions completed today.
    static func sessionsToday(_ sessions: [Session], now: Date = Date()) -> Int {
        focusSessions(in: sessions, day: now).count
    }

    /// Focus minutes completed today.
    static func minutesToday(_ sessions: [Session], now: Date = Date()) -> Int {
        focusSessions(in: sessions, day: now).reduce(0) { $0 + $1.minutes }
    }

    /// (sessions, minutes) completed in the last 7 days incl. today.
    static func thisWeek(_ sessions: [Session],
                         now: Date = Date()) -> (sessions: Int, minutes: Int) {
        let start = calendar.date(byAdding: .day, value: -6,
                                  to: calendar.startOfDay(for: now))!
        let week = sessions.filter { $0.type.isFocus && $0.completedAt >= start }
        return (week.count, week.reduce(0) { $0 + $1.minutes })
    }

    /// (sessions, minutes) completed in the last 30 days incl. today.
    static func thisMonth(_ sessions: [Session],
                          now: Date = Date()) -> (sessions: Int, minutes: Int) {
        let start = calendar.date(byAdding: .day, value: -29,
                                  to: calendar.startOfDay(for: now))!
        let month = sessions.filter { $0.type.isFocus && $0.completedAt >= start }
        return (month.count, month.reduce(0) { $0 + $1.minutes })
    }

    /// All-time focus session count.
    static func allTimeSessions(_ sessions: [Session]) -> Int {
        sessions.filter { $0.type.isFocus }.count
    }

    /// All-time focus minutes.
    static func allTimeMinutes(_ sessions: [Session]) -> Int {
        sessions.filter { $0.type.isFocus }.reduce(0) { $0 + $1.minutes }
    }

    /// Daily average focus minutes over the last 7 days.
    static func weeklyDailyAverage(_ sessions: [Session], now: Date = Date()) -> Int {
        thisWeek(sessions, now: now).minutes / 7
    }

    /// Current streak: consecutive days (ending today or yesterday) with >=1 focus session.
    static func currentStreak(_ sessions: [Session], now: Date = Date()) -> Int {
        let days = focusDays(sessions)
        guard !days.isEmpty else { return 0 }
        var streak = 0
        var cursor = calendar.startOfDay(for: now)

        // Allow the streak to "still be alive" if the user has done none today.
        if !days.contains(cursor) {
            cursor = calendar.date(byAdding: .day, value: -1, to: cursor)!
            if !days.contains(cursor) { return 0 }
        }
        while days.contains(cursor) {
            streak += 1
            cursor = calendar.date(byAdding: .day, value: -1, to: cursor)!
        }
        return streak
    }

    /// Best streak: longest run of consecutive days with >=1 focus session.
    static func bestStreak(_ sessions: [Session]) -> Int {
        let days = focusDays(sessions).sorted()
        guard !days.isEmpty else { return 0 }
        var best = 1
        var run = 1
        for i in 1..<days.count {
            let prev = days[i - 1]
            let curr = days[i]
            if calendar.date(byAdding: .day, value: 1, to: prev) == curr {
                run += 1
                best = max(best, run)
            } else {
                run = 1
            }
        }
        return best
    }

    /// Builds a `dayCount`-day window (oldest first) of `DayStats` for the heat map.
    static func heatMap(_ sessions: [Session],
                        days dayCount: Int = 90,
                        now: Date = Date()) -> [DayStats] {
        let today = calendar.startOfDay(for: now)
        var byDay: [Date: [Session]] = [:]
        for s in sessions where s.type.isFocus {
            let day = calendar.startOfDay(for: s.completedAt)
            byDay[day, default: []].append(s)
        }
        return (0..<dayCount).reversed().map { offset in
            let day = calendar.date(byAdding: .day, value: -offset, to: today)!
            let items = byDay[day] ?? []
            return DayStats(id: day,
                            date: day,
                            focusSessions: items.count,
                            focusMinutes: items.reduce(0) { $0 + $1.minutes })
        }
    }

    // MARK: - Helpers

    private static func focusSessions(in sessions: [Session], day: Date) -> [Session] {
        let start = calendar.startOfDay(for: day)
        return sessions.filter {
            $0.type.isFocus && calendar.isDate($0.completedAt, inSameDayAs: start)
        }
    }

    /// Set of start-of-day dates that have at least one focus session.
    private static func focusDays(_ sessions: [Session]) -> Set<Date> {
        Set(sessions.filter { $0.type.isFocus }
            .map { calendar.startOfDay(for: $0.completedAt) })
    }
}
