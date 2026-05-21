//
//  StatCard.swift
//  PomodoroFocusTimer
//
//  Reusable rounded card used on the Stats screen.
//

import SwiftUI

/// A single labeled statistics card.
struct StatCard<Content: View>: View {
    let title: LocalizedStringKey
    let systemImage: String
    let accent: Color
    @ViewBuilder let content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label(title, systemImage: systemImage)
                .font(.system(size: 14, weight: .semibold))
                .foregroundStyle(accent)
            content
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(Color.white.opacity(0.07), in: RoundedRectangle(cornerRadius: 16))
    }
}

/// A "big number + caption" metric row used inside `StatCard`.
struct Metric: View {
    let value: String
    let caption: LocalizedStringKey

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(value)
                .font(.system(size: 28, weight: .bold, design: .rounded))
                .monospacedDigit()
            Text(caption)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .accessibilityElement(children: .combine)
    }
}
