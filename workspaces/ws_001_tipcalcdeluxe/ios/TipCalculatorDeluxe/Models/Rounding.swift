import Foundation

/// Rounding mode applied to the final total bill.
enum Rounding: String, CaseIterable, Identifiable, Codable {
    case none
    case down
    case up

    var id: String { rawValue }

    /// Short label shown in the segmented control.
    var label: String {
        switch self {
        case .none: return "Exact"
        case .down: return "Round Down"
        case .up: return "Round Up"
        }
    }

    /// Apply the rounding to a grand total (in currency units).
    func apply(to total: Double) -> Double {
        switch self {
        case .none: return total
        case .down: return total.rounded(.down)
        case .up: return total.rounded(.up)
        }
    }
}
