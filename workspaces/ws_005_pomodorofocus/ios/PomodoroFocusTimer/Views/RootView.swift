//
//  RootView.swift
//  PomodoroFocusTimer
//
//  Top-level tab container (Timer / Stats) and lifecycle bridge.
//

import SwiftUI

struct RootView: View {
    @EnvironmentObject private var settings: AppSettings
    @EnvironmentObject private var engine: TimerEngine
    @Environment(\.scenePhase) private var scenePhase

    var body: some View {
        TabView {
            TimerView()
                .tabItem {
                    Label("tab.timer", systemImage: "timer")
                }
            StatsView()
                .tabItem {
                    Label("tab.stats", systemImage: "chart.bar.fill")
                }
        }
        .tint(Color.appAccent)
        .background(AppBackground(trueBlack: settings.trueBlackMode))
        .onChange(of: scenePhase) { phase in
            // Recompute the date-driven timer whenever we cross the
            // foreground / background boundary.
            switch phase {
            case .active:     engine.handleForeground()
            case .background: engine.handleBackground()
            default:          break
            }
        }
    }
}

#Preview {
    RootView()
        .environmentObject(SessionStore.shared)
        .environmentObject(AppSettings())
        .environmentObject(TimerEngine(settings: AppSettings(), store: SessionStore.shared))
}
