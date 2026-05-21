//
//  NotificationManager.swift
//  PomodoroFocusTimer
//
//  Schedules the single "timer finished" local notification using a
//  UNTimeIntervalNotificationTrigger, per spec.technical_notes.
//

import UserNotifications

/// Wraps `UNUserNotificationCenter` for the timer-end alert.
struct NotificationManager {

    /// Identifier reused so a reschedule replaces the previous request.
    private static let timerID = "pomodoro.timer.end"

    private var center: UNUserNotificationCenter { .current() }

    /// Requests notification authorization. Safe to call repeatedly.
    func requestAuthorization(completion: ((Bool) -> Void)? = nil) {
        center.requestAuthorization(options: [.alert, .sound, .badge]) { granted, _ in
            DispatchQueue.main.async { completion?(granted) }
        }
    }

    /// Returns the current authorization status.
    func authorizationStatus(completion: @escaping (UNAuthorizationStatus) -> Void) {
        center.getNotificationSettings { settings in
            DispatchQueue.main.async { completion(settings.authorizationStatus) }
        }
    }

    /// Schedules a notification to fire when the running phase ends.
    /// - Parameters:
    ///   - interval: seconds from now until the phase finishes.
    ///   - endingPhase: the phase that is ending (drives the message text).
    func scheduleTimerNotification(after interval: TimeInterval,
                                   endingPhase: PomodoroPhase) {
        cancelTimerNotification()
        guard interval > 0 else { return }

        let content = UNMutableNotificationContent()
        content.sound = .default
        content.interruptionLevel = .timeSensitive

        switch endingPhase {
        case .focus:
            content.title = NSLocalizedString("notif.focusDone.title", comment: "")
            content.body = NSLocalizedString("notif.focusDone.body", comment: "")
        case .shortBreak, .longBreak:
            content.title = NSLocalizedString("notif.breakDone.title", comment: "")
            content.body = NSLocalizedString("notif.breakDone.body", comment: "")
        }

        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: interval,
                                                        repeats: false)
        let request = UNNotificationRequest(identifier: Self.timerID,
                                            content: content,
                                            trigger: trigger)
        center.add(request)
    }

    /// Cancels any pending timer-end notification (on pause / reset / skip).
    func cancelTimerNotification() {
        center.removePendingNotificationRequests(withIdentifiers: [Self.timerID])
        center.removeDeliveredNotifications(withIdentifiers: [Self.timerID])
    }
}
