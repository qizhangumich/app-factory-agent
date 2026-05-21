import Foundation

/// Thin wrapper around `NSLocalizedString` so model keys can be resolved for
/// display without each call site repeating the table name.
enum L {
    /// Localized display string for a key in `Localizable.xcstrings`.
    static func string(_ key: String) -> String {
        NSLocalizedString(key, comment: "")
    }
}

extension UnitCategory {
    /// Human-readable, localized category name.
    var localizedName: String { L.string(name) }
}

extension ConvUnit {
    /// Human-readable, localized unit name.
    var localizedName: String { L.string(name) }

    /// "Name (symbol)" for pickers and lists.
    var displayLabel: String { "\(localizedName) (\(symbol))" }
}
