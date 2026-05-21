import SwiftUI

/// Classification of a sound level into safe / moderate / dangerous bands.
/// Thresholds follow the spec color scheme: <70 dB safe, 70-85 dB moderate, >85 dB dangerous.
enum NoiseLevel: String {
    case safe
    case moderate
    case danger

    /// Lowest dB value still considered measurable noise floor for the gauge.
    static let minDB: Double = 0
    /// Highest dB value the gauge displays.
    static let maxDB: Double = 130

    init(db: Double) {
        switch db {
        case ..<70:
            self = .safe
        case 70..<85:
            self = .moderate
        default:
            self = .danger
        }
    }

    var color: Color {
        switch self {
        case .safe:     return Color(red: 0x34 / 255, green: 0xC7 / 255, blue: 0x59 / 255) // #34C759
        case .moderate: return Color(red: 0xFF / 255, green: 0x95 / 255, blue: 0x00 / 255) // #FF9500
        case .danger:   return Color(red: 0xFF / 255, green: 0x3B / 255, blue: 0x30 / 255) // #FF3B30
        }
    }

    /// Localized short label for the level.
    var labelKey: LocalizedStringKey {
        switch self {
        case .safe:     return "level.safe"
        case .moderate: return "level.moderate"
        case .danger:   return "level.danger"
        }
    }
}
