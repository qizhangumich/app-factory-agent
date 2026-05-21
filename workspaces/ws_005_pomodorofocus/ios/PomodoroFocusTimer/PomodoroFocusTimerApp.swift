//
//  PomodoroFocusTimerApp.swift
//  PomodoroFocusTimer
//
//  Entry point. Wires the Core Data stack, timer engine and settings
//  into the SwiftUI environment.
//

import SwiftUI
import UserNotifications

@main
struct PomodoroFocusTimerApp: App {
    /// Single source of persistence — a programmatically-built Core Data stack.
    @StateObject private var store = SessionStore.shared
    /// User-configurable timer parameters, persisted in UserDefaults.
    @StateObject private var settings = AppSettings()
    /// Date-driven timer engine (no background Timer; see TimerEngine docs).
    @StateObject private var engine: TimerEngine

    init() {
        let settings = AppSettings()
        _settings = StateObject(wrappedValue: settings)
        _engine = StateObject(wrappedValue: TimerEngine(settings: settings,
                                                        store: SessionStore.shared))
        // Become the notification delegate so banners show while in foreground.
        UNUserNotificationCenter.current().delegate = NotificationDelegate.shared
    }

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(store)
                .environmentObject(settings)
                .environmentObject(engine)
                .preferredColorScheme(.dark)
                .tint(Color.appAccent)
        }
    }
}

/// Forwards notification presentation so the timer-end alert is visible
/// even when the app is open.
final class NotificationDelegate: NSObject, UNUserNotificationCenterDelegate {
    static let shared = NotificationDelegate()

    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                willPresent notification: UNNotification,
                                withCompletionHandler completionHandler:
                                @escaping (UNNotificationPresentationOptions) -> Void) {
        completionHandler([.banner, .sound, .list])
    }
}
