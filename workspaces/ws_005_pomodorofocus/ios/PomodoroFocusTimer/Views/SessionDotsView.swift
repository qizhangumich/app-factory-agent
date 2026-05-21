//
//  SessionDotsView.swift
//  PomodoroFocusTimer
//
//  Row of dots showing progress toward the next long break
//  (filled = completed focus session).
//

import SwiftUI

/// Session progress dots: ● ● ○ ○ (spec: TimerView component 4).
struct SessionDotsView: View {
    /// Number of focus sessions completed in the current cycle.
    let completed: Int
    /// Total dots = sessions until a long break.
    let total: Int
    /// Color used for the filled dots.
    let color: Color

    var body: some View {
        HStack(spacing: 12) {
            ForEach(0..<max(total, 1), id: \.self) { index in
                Circle()
                    .fill(index < completed ? color : Color.white.opacity(0.18))
                    .frame(width: 12, height: 12)
                    .overlay(
                        Circle()
                            .stroke(color.opacity(index < completed ? 0 : 0.4),
                                    lineWidth: 1)
                    )
                    .animation(.spring(response: 0.3), value: completed)
            }
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(Text("a11y.sessionProgress"))
        .accessibilityValue(Text("\(completed) / \(total)"))
    }
}

#Preview {
    SessionDotsView(completed: 2, total: 4, color: Color(hex: 0xFF6B6B))
        .padding()
        .preferredColorScheme(.dark)
}
