//
//  HeatMapView.swift
//  PomodoroFocusTimer
//
//  GitHub-contribution-style 90-day calendar heat map.
//

import SwiftUI

/// Renders a grid of day cells colored by focus-session count.
struct HeatMapView: View {
    /// Oldest-first list of per-day stats (typically 90 entries).
    let days: [DayStats]

    private let cell: CGFloat = 14
    private let spacing: CGFloat = 3
    private let rows = 7   // one column per week, Mon..Sun

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            ScrollViewReader { proxy in
                ScrollView(.horizontal, showsIndicators: false) {
                    LazyHGrid(rows: gridRows, spacing: spacing) {
                        ForEach(days) { day in
                            RoundedRectangle(cornerRadius: 3)
                                .fill(Color.heatColor(level: level(for: day)))
                                .frame(width: cell, height: cell)
                                .id(day.id)
                                .accessibilityLabel(Text(accessibilityText(day)))
                        }
                    }
                    .padding(.vertical, 2)
                }
                .onAppear {
                    if let last = days.last?.id {
                        proxy.scrollTo(last, anchor: .trailing)
                    }
                }
            }
            legend
        }
    }

    private var gridRows: [GridItem] {
        Array(repeating: GridItem(.fixed(cell), spacing: spacing), count: rows)
    }

    /// Maps session count to a 0...4 intensity level.
    private func level(for day: DayStats) -> Int {
        switch day.focusSessions {
        case 0:     return 0
        case 1:     return 1
        case 2...3: return 2
        case 4...5: return 3
        default:    return 4
        }
    }

    private func accessibilityText(_ day: DayStats) -> String {
        let df = DateFormatter()
        df.dateStyle = .medium
        let date = df.string(from: day.date)
        let fmt = NSLocalizedString("a11y.heatCell", comment: "")
        return String(format: fmt, date, day.focusSessions)
    }

    private var legend: some View {
        HStack(spacing: 6) {
            Text("stats.less")
                .font(.caption2)
                .foregroundStyle(.secondary)
            ForEach(0..<5, id: \.self) { lvl in
                RoundedRectangle(cornerRadius: 2)
                    .fill(Color.heatColor(level: lvl))
                    .frame(width: 11, height: 11)
            }
            Text("stats.more")
                .font(.caption2)
                .foregroundStyle(.secondary)
        }
    }
}

#Preview {
    HeatMapView(days: (0..<90).map {
        DayStats(id: Date(),
                 date: Date(),
                 focusSessions: Int.random(in: 0...6),
                 focusMinutes: 0)
    })
    .padding()
    .preferredColorScheme(.dark)
}
