//
//  Theme.swift
//  QRBarcodeScanner
//
//  Shared colors and small formatting helpers.
//

import SwiftUI

extension Color {
    /// Green used to flash the reticle / badges on a successful scan
    /// (spec color_scheme.scan_success = #34C759).
    static let scanSuccess = Color(red: 0x34 / 255.0,
                                   green: 0xC7 / 255.0,
                                   blue: 0x59 / 255.0)

    /// Primary accent (system blue).
    static let appPrimary = Color.blue
}

enum DateFormatting {
    /// Shared, locale-aware medium-date / short-time formatter.
    static let scanTimestamp: DateFormatter = {
        let f = DateFormatter()
        f.dateStyle = .medium
        f.timeStyle = .short
        return f
    }()

    /// Relative formatter ("2 hours ago") for compact rows.
    static let relative: RelativeDateTimeFormatter = {
        let f = RelativeDateTimeFormatter()
        f.unitsStyle = .abbreviated
        return f
    }()
}
