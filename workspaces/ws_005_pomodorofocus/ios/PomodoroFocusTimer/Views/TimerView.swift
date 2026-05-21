//
//  TimerView.swift
//  PomodoroFocusTimer
//
//  Main screen: circular timer, session dots, transport controls and a
//  gear that presents Settings as a sheet.
//

import SwiftUI

struct TimerView: View {
    @EnvironmentObject private var engine: TimerEngine
    @EnvironmentObject private var settings: AppSettings

    @State private var showSettings = false

    var body: some View {
        NavigationStack {
            ZStack {
                AppBackground(trueBlack: settings.trueBlackMode)

                VStack(spacing: 36) {
                    Spacer(minLength: 8)

                    TimerRingView(progress: engine.progress,
                                  timeText: engine.timeString,
                                  phaseLabel: engine.phase.displayName,
                                  phaseColor: engine.phase.color)

                    SessionDotsView(completed: cycleCompleted,
                                    total: engine.cycleLength,
                                    color: engine.phase.color)

                    controls

                    Spacer()
                }
                .padding(.horizontal, 24)
            }
            .navigationTitle("app.name")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        Haptics.selection()
                        showSettings = true
                    } label: {
                        Image(systemName: "gearshape.fill")
                    }
                    .accessibilityLabel(Text("a11y.openSettings"))
                }
            }
            .sheet(isPresented: $showSettings) {
                SettingsView()
            }
        }
    }

    /// Dots fill up to the cycle length; the engine resets the counter
    /// after a long break.
    private var cycleCompleted: Int {
        min(engine.completedInCycle, max(engine.cycleLength, 1))
    }

    // MARK: - Controls

    private var controls: some View {
        VStack(spacing: 18) {
            // Primary Start / Pause.
            Button {
                Haptics.medium()
                engine.startOrPause()
            } label: {
                Text(primaryLabel)
                    .font(.system(size: 20, weight: .bold))
                    .frame(maxWidth: .infinity)
                    .frame(height: 58)
                    .background(engine.phase.color, in: Capsule())
                    .foregroundStyle(.white)
            }
            .accessibilityLabel(Text(primaryLabel))

            // Secondary Reset / Skip.
            HStack(spacing: 16) {
                secondaryButton(titleKey: "control.reset",
                                systemImage: "arrow.counterclockwise") {
                    engine.reset()
                }
                secondaryButton(titleKey: "control.skip",
                                systemImage: "forward.end.fill") {
                    engine.skip()
                }
            }
        }
    }

    private func secondaryButton(titleKey: LocalizedStringKey,
                                 systemImage: String,
                                 action: @escaping () -> Void) -> some View {
        Button {
            Haptics.light()
            action()
        } label: {
            Label(titleKey, systemImage: systemImage)
                .font(.system(size: 16, weight: .semibold))
                .frame(maxWidth: .infinity)
                .frame(height: 48)
                .background(Color.white.opacity(0.10), in: Capsule())
                .foregroundStyle(.primary)
        }
    }

    private var primaryLabel: LocalizedStringKey {
        switch engine.runState {
        case .running: return "control.pause"
        case .paused:  return "control.resume"
        case .idle:    return "control.start"
        }
    }
}

#Preview {
    TimerView()
        .environmentObject(SessionStore.shared)
        .environmentObject(AppSettings())
        .environmentObject(TimerEngine(settings: AppSettings(), store: SessionStore.shared))
        .preferredColorScheme(.dark)
}
