//
//  Theme.swift
//  PomodoroFocusTimer
//
//  Color helpers and haptic shortcuts shared across the UI.
//

import SwiftUI
import UIKit

extension Color {
    /// Builds a `Color` from a 0xRRGGBB integer literal.
    init(hex: UInt32) {
        let r = Double((hex >> 16) & 0xFF) / 255.0
        let g = Double((hex >> 8) & 0xFF) / 255.0
        let b = Double(hex & 0xFF) / 255.0
        self.init(.sRGB, red: r, green: g, blue: b, opacity: 1)
    }

    /// App accent — the warm pomodoro red.
    static let appAccent = Color(hex: 0xFF6B6B)

    /// Heat-map green ramp. `level` 0 = none, 4 = most.
    static func heatColor(level: Int) -> Color {
        switch level {
        case 0:  return Color.white.opacity(0.08)
        case 1:  return Color(hex: 0x2E5E2E)
        case 2:  return Color(hex: 0x3B8C3B)
        case 3:  return Color(hex: 0x4FBF4F)
        default: return Color(hex: 0x6BE86B)
        }
    }
}

/// Resolves the screen background, honoring the true-black OLED setting.
struct AppBackground: View {
    let trueBlack: Bool
    var body: some View {
        Group {
            if trueBlack {
                Color.black
            } else {
                Color(UIColor.systemBackground)
            }
        }
        .ignoresSafeArea()
    }
}

/// Thin wrapper over UIKit haptic generators.
enum Haptics {
    static func light() {
        UIImpactFeedbackGenerator(style: .light).impactOccurred()
    }
    static func medium() {
        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
    }
    static func success() {
        UINotificationFeedbackGenerator().notificationOccurred(.success)
    }
    static func selection() {
        UISelectionFeedbackGenerator().selectionChanged()
    }
}
