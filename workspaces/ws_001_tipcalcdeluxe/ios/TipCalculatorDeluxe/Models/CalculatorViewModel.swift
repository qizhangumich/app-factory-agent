import Foundation
import Combine

/// Drives the single-screen calculator. Holds all user input, derives the
/// live result, and commits finished calculations into `HistoryStore`.
final class CalculatorViewModel: ObservableObject {

    // MARK: User input

    /// Raw text of the bill amount field (kept as text so the field can be empty).
    @Published var billText: String = ""

    /// Tip percentage, 0...50 (spec: slider 0-50%, default 18%).
    @Published var tipPercent: Double = 18

    /// Whether tax is included in the total (spec: default off).
    @Published var taxEnabled: Bool = false

    /// Tax rate text, used when `taxEnabled` is true.
    @Published var taxText: String = "8"

    /// Number of people to split between, 1...20 (spec: default 2).
    @Published var people: Int = 2

    /// Equal vs. unequal split mode.
    @Published var isUnequalSplit: Bool = false

    /// Per-person weights when `isUnequalSplit` is true. Always `people` long.
    @Published var customWeights: [Double] = [1, 1]

    /// Rounding mode applied to the grand total.
    @Published var rounding: Rounding = .none

    // MARK: Limits

    let minPeople = 1
    let maxPeople = 20
    let minTip: Double = 0
    let maxTip: Double = 50

    // MARK: Derived input

    var billAmount: Double { CurrencyFormatter.parse(billText) }
    var taxPercent: Double {
        let value = CurrencyFormatter.parse(taxText)
        return max(0, value)
    }

    /// Whether there is a usable bill amount to calculate from.
    var hasBill: Bool { billAmount > 0 }

    // MARK: Derived result

    /// The current calculation snapshot (not yet persisted).
    var calculation: TipCalculation {
        TipCalculation(
            billAmount: billAmount,
            tipPercent: tipPercent,
            taxEnabled: taxEnabled,
            taxPercent: taxPercent,
            people: people,
            isUnequalSplit: isUnequalSplit,
            rounding: rounding
        )
    }

    var tipAmount: Double { calculation.tipAmount }
    var taxAmount: Double { calculation.taxAmount }
    var grandTotal: Double { calculation.grandTotal }
    var totalPerPerson: Double { calculation.totalPerPerson }
    var tipPerPerson: Double { calculation.tipPerPerson }
    var taxPerPerson: Double { calculation.taxPerPerson }

    /// Sum of the custom weights, used to divide the unequal split.
    var weightTotal: Double {
        let sum = customWeights.reduce(0, +)
        return sum > 0 ? sum : 1
    }

    /// Amount owed by a given person index for an unequal split.
    func unequalShare(for index: Int) -> Double {
        guard index >= 0, index < customWeights.count else { return 0 }
        return grandTotal * customWeights[index] / weightTotal
    }

    // MARK: People management

    /// Increase the number of people, clamped to `maxPeople`.
    func incrementPeople() {
        guard people < maxPeople else { return }
        people += 1
        syncWeights()
        Haptics.light()
    }

    /// Decrease the number of people, clamped to `minPeople`.
    func decrementPeople() {
        guard people > minPeople else { return }
        people -= 1
        syncWeights()
        Haptics.light()
    }

    /// Keep `customWeights` exactly `people` entries long.
    func syncWeights() {
        if customWeights.count < people {
            customWeights.append(contentsOf: Array(repeating: 1, count: people - customWeights.count))
        } else if customWeights.count > people {
            customWeights = Array(customWeights.prefix(people))
        }
    }

    /// Update one person's weight (used by the unequal-split editor).
    func setWeight(_ value: Double, at index: Int) {
        syncWeights()
        guard index >= 0, index < customWeights.count else { return }
        customWeights[index] = max(0, value)
    }

    // MARK: Actions

    /// Persist the current calculation to history.
    /// Returns `true` when a calculation was actually saved.
    @discardableResult
    func saveToHistory(_ store: HistoryStore) -> Bool {
        guard hasBill else { return false }
        store.add(calculation)
        Haptics.success()
        return true
    }

    /// Restore the calculator inputs from a history entry.
    func restore(from entry: TipCalculation) {
        billText = String(format: "%.2f", entry.billAmount)
        tipPercent = min(max(entry.tipPercent, minTip), maxTip)
        taxEnabled = entry.taxEnabled
        taxText = String(format: "%g", entry.taxPercent)
        people = min(max(entry.people, minPeople), maxPeople)
        isUnequalSplit = entry.isUnequalSplit
        rounding = entry.rounding
        syncWeights()
        Haptics.medium()
    }

    /// Reset every input back to its default state.
    func reset() {
        billText = ""
        tipPercent = 18
        taxEnabled = false
        taxText = "8"
        people = 2
        isUnequalSplit = false
        customWeights = [1, 1]
        rounding = .none
        Haptics.light()
    }
}
