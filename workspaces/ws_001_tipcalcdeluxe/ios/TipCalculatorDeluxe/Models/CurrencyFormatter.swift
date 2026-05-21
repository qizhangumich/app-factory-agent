import Foundation

/// Locale-aware currency formatting. The currency symbol is auto-detected
/// from the device locale (spec: "Currency symbol auto-detection from locale").
enum CurrencyFormatter {

    /// Shared formatter configured for the current locale.
    private static let formatter: NumberFormatter = {
        let f = NumberFormatter()
        f.numberStyle = .currency
        f.locale = Locale.current
        f.maximumFractionDigits = 2
        f.minimumFractionDigits = 2
        return f
    }()

    /// The currency symbol for the current locale (e.g. "$", "£", "AED").
    static var symbol: String {
        formatter.currencySymbol ?? Locale.current.currency?.identifier ?? "$"
    }

    /// Format a monetary value using the current locale's currency style.
    static func string(from value: Double) -> String {
        let safe = value.isFinite ? value : 0
        return formatter.string(from: NSNumber(value: safe)) ?? "\(symbol)0.00"
    }

    /// Parse a free-form numeric string (the bill / tax input fields).
    /// Strips the currency symbol, grouping separators and whitespace.
    static func parse(_ text: String) -> Double {
        var cleaned = text
        if let groupingSeparator = formatter.groupingSeparator {
            cleaned = cleaned.replacingOccurrences(of: groupingSeparator, with: "")
        }
        cleaned = cleaned.replacingOccurrences(of: symbol, with: "")
        cleaned = cleaned.trimmingCharacters(in: .whitespacesAndNewlines)
        // Normalise the locale decimal separator to a dot for Double parsing.
        if let decimalSeparator = formatter.decimalSeparator, decimalSeparator != "." {
            cleaned = cleaned.replacingOccurrences(of: decimalSeparator, with: ".")
        }
        return Double(cleaned) ?? 0
    }
}
