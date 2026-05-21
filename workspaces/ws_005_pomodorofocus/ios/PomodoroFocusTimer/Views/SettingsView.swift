//
//  SettingsView.swift
//  PomodoroFocusTimer
//
//  Sheet presented from TimerView to configure every timer parameter.
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject private var settings: AppSettings
    @EnvironmentObject private var store: SessionStore
    @Environment(\.dismiss) private var dismiss

    @State private var showResetStatsAlert = false
    @State private var notifStatusDenied = false

    private let notifications = NotificationManager()

    var body: some View {
        NavigationStack {
            Form {
                durationsSection
                cycleSection
                behaviorSection
                soundSection
                appearanceSection
                dataSection
                aboutSection
            }
            .navigationTitle("settings.title")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("settings.done") { dismiss() }
                        .fontWeight(.semibold)
                }
            }
            .onAppear(perform: refreshNotificationStatus)
            .alert("settings.resetStats.title", isPresented: $showResetStatsAlert) {
                Button("settings.resetStats.confirm", role: .destructive) {
                    store.deleteAll()
                }
                Button("common.cancel", role: .cancel) { }
            } message: {
                Text("settings.resetStats.message")
            }
        }
    }

    // MARK: - Durations

    private var durationsSection: some View {
        Section("settings.section.durations") {
            stepperRow(title: "settings.focusDuration",
                       value: $settings.focusMinutes,
                       range: settings.focusRange,
                       systemImage: "brain.head.profile",
                       tint: PomodoroPhase.focus.color)
            stepperRow(title: "settings.shortBreak",
                       value: $settings.shortBreakMinutes,
                       range: settings.shortBreakRange,
                       systemImage: "cup.and.saucer.fill",
                       tint: PomodoroPhase.shortBreak.color)
            stepperRow(title: "settings.longBreak",
                       value: $settings.longBreakMinutes,
                       range: settings.longBreakRange,
                       systemImage: "bed.double.fill",
                       tint: PomodoroPhase.longBreak.color)
        }
    }

    private var cycleSection: some View {
        Section("settings.section.cycle") {
            Stepper(value: $settings.sessionsUntilLongBreak,
                    in: settings.cycleRange) {
                Label {
                    HStack {
                        Text("settings.sessionsUntilLong")
                        Spacer()
                        Text("\(settings.sessionsUntilLongBreak)")
                            .foregroundStyle(.secondary)
                            .monospacedDigit()
                    }
                } icon: {
                    Image(systemName: "repeat")
                }
            }
            .onChange(of: settings.sessionsUntilLongBreak) { _ in Haptics.selection() }
        }
    }

    private var behaviorSection: some View {
        Section("settings.section.behavior") {
            Toggle(isOn: $settings.autoStartNext) {
                Label("settings.autoStart", systemImage: "play.circle.fill")
            }
        }
    }

    // MARK: - Sound

    private var soundSection: some View {
        Section("settings.section.sound") {
            Picker(selection: $settings.focusSound) {
                ForEach(FocusSound.allCases) { sound in
                    Text(sound.displayName).tag(sound)
                }
            } label: {
                Label("settings.focusSound", systemImage: "speaker.wave.2.fill")
            }
            .pickerStyle(.navigationLink)
        }
    }

    // MARK: - Appearance & notifications

    private var appearanceSection: some View {
        Section {
            Toggle(isOn: $settings.notificationsEnabled) {
                Label("settings.notifications", systemImage: "bell.badge.fill")
            }
            .onChange(of: settings.notificationsEnabled) { enabled in
                if enabled {
                    notifications.requestAuthorization { granted in
                        notifStatusDenied = !granted
                    }
                }
            }
            if notifStatusDenied && settings.notificationsEnabled {
                Text("settings.notifications.denied")
                    .font(.footnote)
                    .foregroundStyle(.orange)
            }
            Toggle(isOn: $settings.trueBlackMode) {
                Label("settings.trueBlack", systemImage: "moon.stars.fill")
            }
        } header: {
            Text("settings.section.appearance")
        } footer: {
            Text("settings.trueBlack.footer")
        }
    }

    // MARK: - Data

    private var dataSection: some View {
        Section("settings.section.data") {
            Button(role: .destructive) {
                showResetStatsAlert = true
            } label: {
                Label("settings.resetStats", systemImage: "trash.fill")
            }
        }
    }

    private var aboutSection: some View {
        Section("settings.section.about") {
            HStack {
                Text("settings.version")
                Spacer()
                Text(appVersion).foregroundStyle(.secondary)
            }
            HStack {
                Text("settings.technique")
                Spacer()
                Text("settings.technique.value").foregroundStyle(.secondary)
            }
        }
    }

    // MARK: - Helpers

    private func stepperRow(title: LocalizedStringKey,
                            value: Binding<Int>,
                            range: ClosedRange<Int>,
                            systemImage: String,
                            tint: Color) -> some View {
        Stepper(value: value, in: range) {
            Label {
                HStack {
                    Text(title)
                    Spacer()
                    Text(minuteText(value.wrappedValue))
                        .foregroundStyle(.secondary)
                        .monospacedDigit()
                }
            } icon: {
                Image(systemName: systemImage).foregroundStyle(tint)
            }
        }
        .onChange(of: value.wrappedValue) { _ in Haptics.selection() }
    }

    private func minuteText(_ minutes: Int) -> String {
        let fmt = NSLocalizedString("settings.minuteValue", comment: "")
        return String(format: fmt, minutes)
    }

    private func refreshNotificationStatus() {
        notifications.authorizationStatus { status in
            notifStatusDenied = (status == .denied)
        }
    }

    private var appVersion: String {
        let v = Bundle.main.infoDictionary?["CFBundleShortVersionString"]
            as? String ?? "1.0.0"
        let b = Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "1"
        return "\(v) (\(b))"
    }
}

#Preview {
    SettingsView()
        .environmentObject(AppSettings())
        .environmentObject(SessionStore.shared)
        .preferredColorScheme(.dark)
}
