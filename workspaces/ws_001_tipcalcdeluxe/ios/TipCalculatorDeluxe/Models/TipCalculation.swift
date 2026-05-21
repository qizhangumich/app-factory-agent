import Foundation

/// A single immutable result of a tip calculation, persisted into history.
struct TipCalculation: Identifiable, Codable, Equatable {
    var id: UUID = UUID()
    var date: Date = Date()

    /// Raw bill amount entered by the user (pre-tip, pre-tax).
    var billAmount: Double
    /// Tip percentage applied (0...50).
    var tipPercent: Double
    /// Whether tax was included.
    var taxEnabled: Bool
    /// Tax percentage applied when `taxEnabled` is true.
    var taxPercent: Double
    /// Number of people the bill was split between.
    var people: Int
    /// Whether the split was equal or unequal.
    var isUnequalSplit: Bool
    /// Rounding mode applied to the grand total.
    var rounding: Rounding

    // MARK: Derived values

    var tipAmount: Double { billAmount * tipPercent / 100.0 }
    var taxAmount: Double { taxEnabled ? billAmount * taxPercent / 100.0 : 0.0 }

    /// Grand total before rounding.
    var rawTotal: Double { billAmount + tipAmount + taxAmount }

    /// Grand total after the rounding mode is applied.
    var grandTotal: Double { rounding.apply(to: rawTotal) }

    var totalPerPerson: Double {
        guard people > 0 else { return 0 }
        return grandTotal / Double(people)
    }

    var tipPerPerson: Double {
        guard people > 0 else { return 0 }
        return tipAmount / Double(people)
    }

    var taxPerPerson: Double {
        guard people > 0 else { return 0 }
        return taxAmount / Double(people)
    }
}
