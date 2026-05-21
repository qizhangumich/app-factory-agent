//
//  HapticEngine.swift
//  QRBarcodeScanner
//
//  Thin wrapper over UIKit feedback generators for scan confirmation.
//

import UIKit

enum HapticEngine {

    /// Fires a success notification haptic (used on a successful scan).
    @MainActor
    static func success() {
        let generator = UINotificationFeedbackGenerator()
        generator.prepare()
        generator.notificationOccurred(.success)
    }

    /// Fires a light selection tick (used for minor UI confirmations).
    @MainActor
    static func tick() {
        let generator = UISelectionFeedbackGenerator()
        generator.prepare()
        generator.selectionChanged()
    }
}
