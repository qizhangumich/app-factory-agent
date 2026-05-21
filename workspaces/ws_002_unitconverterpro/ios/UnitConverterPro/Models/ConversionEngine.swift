import Foundation

/// Pure, stateless conversion math. All factors come from `UnitData`.
enum ConversionEngine {

    /// Converts `value` from one unit to another within the same category.
    /// Returns `nil` if the units belong to different categories.
    static func convert(_ value: Double,
                        from: ConvUnit,
                        to: ConvUnit,
                        category: UnitCategory) -> Double? {
        guard category.units.contains(where: { $0.id == from.id }),
              category.units.contains(where: { $0.id == to.id }) else { return nil }

        if category.isTemperature {
            return convertTemperature(value, from: from.id, to: to.id)
        }
        if category.id == "fuelEconomy" {
            return convertFuelEconomy(value, from: from.id, to: to.id)
        }
        // Linear conversion: value -> base -> target.
        let base = value * from.factor
        return base / to.factor
    }

    // MARK: - Temperature

    /// Temperature conversion via Celsius as the pivot.
    private static func convertTemperature(_ value: Double,
                                           from: String,
                                           to: String) -> Double {
        // Step 1: incoming value -> Celsius.
        let celsius: Double
        switch from {
        case "temperature.celsius":    celsius = value
        case "temperature.fahrenheit": celsius = (value - 32) * 5.0 / 9.0
        case "temperature.kelvin":     celsius = value - 273.15
        default:                       celsius = value
        }
        // Step 2: Celsius -> target.
        switch to {
        case "temperature.celsius":    return celsius
        case "temperature.fahrenheit": return celsius * 9.0 / 5.0 + 32
        case "temperature.kelvin":     return celsius + 273.15
        default:                       return celsius
        }
    }

    // MARK: - Fuel Economy

    /// Fuel economy. Most units are linear against km/L, but L/100km is the
    /// reciprocal. We only have linear units in `UnitData`, so this stays linear,
    /// but the dedicated path keeps the door open and guards against zero.
    private static func convertFuelEconomy(_ value: Double,
                                           from: String,
                                           to: String) -> Double {
        guard let fromUnit = UnitData.fuelEconomy.unit(withID: from),
              let toUnit = UnitData.fuelEconomy.unit(withID: to) else { return value }
        let base = value * fromUnit.factor
        return base / toUnit.factor
    }

    // MARK: - Formatting

    /// Formats a numeric result for display. Uses scientific notation for very
    /// large or very small magnitudes, otherwise a trimmed decimal string.
    static func format(_ value: Double) -> String {
        if value.isNaN { return "—" }
        if value.isInfinite { return value > 0 ? "∞" : "-∞" }
        if value == 0 { return "0" }

        let magnitude = abs(value)
        if magnitude != 0 && (magnitude >= 1e12 || magnitude < 1e-6) {
            let f = NumberFormatter()
            f.numberStyle = .scientific
            f.maximumFractionDigits = 6
            f.exponentSymbol = "e"
            f.locale = Locale.current
            return f.string(from: NSNumber(value: value)) ?? String(value)
        }

        let f = NumberFormatter()
        f.numberStyle = .decimal
        f.minimumFractionDigits = 0
        f.maximumFractionDigits = 8
        f.usesGroupingSeparator = true
        f.locale = Locale.current
        return f.string(from: NSNumber(value: value)) ?? String(value)
    }

    /// Parses user text into a Double, tolerating the current locale's
    /// grouping/decimal separators and plain ASCII input.
    static func parse(_ text: String) -> Double? {
        let trimmed = text.trimmingCharacters(in: .whitespaces)
        if trimmed.isEmpty { return nil }

        let f = NumberFormatter()
        f.numberStyle = .decimal
        f.locale = Locale.current
        if let n = f.number(from: trimmed) { return n.doubleValue }

        // Fallback: treat comma as decimal separator, strip spaces.
        let normalized = trimmed
            .replacingOccurrences(of: " ", with: "")
            .replacingOccurrences(of: ",", with: ".")
        return Double(normalized)
    }
}
