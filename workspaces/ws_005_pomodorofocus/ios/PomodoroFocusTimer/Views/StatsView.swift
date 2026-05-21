//
//  StatsView.swift
//  PomodoroFocusTimer
//
//  Statistics screen: 90-day heat map, streak counters and metric cards.
//

import SwiftUI

struct StatsView: View {
    @EnvironmentObject private var store: SessionStore
    @EnvironmentObject private var settings: AppSettings

    var body: some View {
        NavigationStack {
            ZStack {
                AppBackground(trueBlack: settings.trueBlackMode)

                ScrollView {
                    VStack(spacing: 16) {
                        heatCard
                        streakCard
                        todayCard
                        weekCard
                        allTimeCard
                    }
                    .padding(16)
                }
            }
            .navigationTitle("tab.stats")
        }
    }

    // MARK: - Cards

    private var heatCard: some View {
        StatCard(title: "stats.heatmap",
                 systemImage: "square.grid.3x3.fill",
                 accent: Color(hex: 0x4FBF4F)) {
            HeatMapView(days: StatsCalculator.heatMap(store.sessions))
        }
    }

    private var streakCard: some View {
        HStack(spacing: 16) {
            StatCard(title: "stats.currentStreak",
                     systemImage: "flame.fill",
                     accent: Color(hex: 0xFF6B6B)) {
                Metric(value: dayCount(StatsCalculator.currentStreak(store.sessions)),
                       caption: "stats.consecutiveDays")
            }
            StatCard(title: "stats.bestStreak",
                     systemImage: "trophy.fill",
                     accent: Color(hex: 0x45B7D1)) {
                Metric(value: dayCount(StatsCalculator.bestStreak(store.sessions)),
                       caption: "stats.longestRun")
            }
        }
    }

    private var todayCard: some View {
        StatCard(title: "stats.today",
                 systemImage: "sun.max.fill",
                 accent: Color(hex: 0xFF6B6B)) {
            HStack {
                Metric(value: "\(StatsCalculator.sessionsToday(store.sessions))",
                       caption: "stats.sessions")
                Spacer()
                Metric(value: "\(StatsCalculator.minutesToday(store.sessions))",
                       caption: "stats.focusMinutes")
            }
        }
    }

    private var weekCard: some View {
        let week = StatsCalculator.thisWeek(store.sessions)
        return StatCard(title: "stats.thisWeek",
                        systemImage: "calendar",
                        accent: Color(hex: 0x4ECDC4)) {
            HStack {
                Metric(value: "\(week.sessions)", caption: "stats.sessions")
                Spacer()
                Metric(value: "\(week.minutes)", caption: "stats.focusMinutes")
                Spacer()
                Metric(value: "\(StatsCalculator.weeklyDailyAverage(store.sessions))",
                       caption: "stats.dailyAvg")
            }
        }
    }

    private var allTimeCard: some View {
        let month = StatsCalculator.thisMonth(store.sessions)
        return VStack(spacing: 16) {
            StatCard(title: "stats.thisMonth",
                     systemImage: "calendar.badge.clock",
                     accent: Color(hex: 0x45B7D1)) {
                HStack {
                    Metric(value: "\(month.sessions)", caption: "stats.sessions")
                    Spacer()
                    Metric(value: "\(month.minutes)", caption: "stats.focusMinutes")
                }
            }
            StatCard(title: "stats.allTime",
                     systemImage: "infinity",
                     accent: Color(hex: 0x9B8CFF)) {
                HStack {
                    Metric(value: "\(StatsCalculator.allTimeSessions(store.sessions))",
                           caption: "stats.sessions")
                    Spacer()
                    Metric(value: "\(StatsCalculator.allTimeMinutes(store.sessions))",
                           caption: "stats.focusMinutes")
                }
            }
        }
    }

    private func dayCount(_ n: Int) -> String {
        let fmt = NSLocalizedString("stats.dayValue", comment: "")
        return String(format: fmt, n)
    }
}

#Preview {
    StatsView()
        .environmentObject(SessionStore.shared)
        .environmentObject(AppSettings())
        .preferredColorScheme(.dark)
}
