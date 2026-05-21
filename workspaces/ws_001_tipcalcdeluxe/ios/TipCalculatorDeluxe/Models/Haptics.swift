import UIKit

/// Lightweight wrapper around UIKit haptic generators
/// (spec feature: "Haptic feedback on interactions").
enum Haptics {

    /// A soft tap — used for sliders, steppers and toggles.
    static func light() {
        let generator = UIImpactFeedbackGenerator(style: .light)
        generator.prepare()
        generator.impactOccurred()
    }

    /// A firmer tap — used when committing a calculation to history.
    static func medium() {
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.prepare()
        generator.impactOccurred()
    }

    /// A success notification — used when a calculation is saved.
    static func success() {
        let generator = UINotificationFeedbackGenerator()
        generator.prepare()
        generator.notificationOccurred(.success)
    }

    /// A selection change — used for segmented controls.
    static func selection() {
        let generator = UISelectionFeedbackGenerator()
        generator.prepare()
        generator.selectionChanged()
    }
}
