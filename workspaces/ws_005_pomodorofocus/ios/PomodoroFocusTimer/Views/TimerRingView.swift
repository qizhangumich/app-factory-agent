//
//  TimerRingView.swift
//  PomodoroFocusTimer
//
//  The large circular progress ring with the MM:SS label in its center.
//

import SwiftUI

/// 250pt circular progress ring (spec: TimerView component 1 & 2).
struct TimerRingView: View {
    /// 0...1 elapsed fraction.
    let progress: Double
    /// "MM:SS" text shown in the center.
    let timeText: String
    /// Localized phase label shown above the time.
    let phaseLabel: LocalizedStringKey
    /// Phase color for the ring stroke and label.
    let phaseColor: Color

    private let diameter: CGFloat = 250
    private let lineWidth: CGFloat = 18

    var body: some View {
        ZStack {
            // Track.
            Circle()
                .stroke(Color.white.opacity(0.10), lineWidth: lineWidth)

            // Progress.
            Circle()
                .trim(from: 0, to: max(0.0001, progress))
                .stroke(
                    phaseColor,
                    style: StrokeStyle(lineWidth: lineWidth, lineCap: .round)
                )
                .rotationEffect(.degrees(-90))
                .animation(.easeInOut(duration: 0.35), value: progress)
                .shadow(color: phaseColor.opacity(0.5), radius: 8)

            VStack(spacing: 6) {
                Text(phaseLabel)
                    .font(.system(size: 15, weight: .bold))
                    .tracking(2)
                    .foregroundStyle(phaseColor)
                Text(timeText)
                    .font(.system(size: 64, weight: .bold, design: .rounded))
                    .monospacedDigit()
                    .foregroundStyle(.primary)
                    .contentTransition(.numericText())
            }
        }
        .frame(width: diameter, height: diameter)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(Text(phaseLabel))
        .accessibilityValue(Text(timeText))
    }
}

#Preview {
    TimerRingView(progress: 0.4,
                  timeText: "15:00",
                  phaseLabel: "phase.focus",
                  phaseColor: Color(hex: 0xFF6B6B))
        .padding()
        .preferredColorScheme(.dark)
}
