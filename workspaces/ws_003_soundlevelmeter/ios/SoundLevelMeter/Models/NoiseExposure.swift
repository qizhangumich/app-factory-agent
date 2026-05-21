import Foundation
import SwiftUI

/// NIOSH noise-exposure calculator.
///
/// NIOSH Recommended Exposure Limit (REL): 85 dBA for 8 hours, with a
/// 3 dB exchange rate — every additional 3 dB halves the permissible
/// exposure time. Below 85 dB exposure is considered safe for a full
/// work day (and beyond).
struct NoiseExposure {
    /// NIOSH reference level in dB.
    static let referenceDB: Double = 85
    /// Reference duration at the reference level, in seconds (8 hours).
    static let referenceSeconds: Double = 8 * 60 * 60
    /// 3 dB exchange rate.
    static let exchangeRate: Double = 3

    /// Permissible exposure time in seconds for a sustained level, or
    /// `nil` when the level is at/below the safe reference (no limit).
    static func permissibleSeconds(forDB db: Double) -> Double? {
        guard db > referenceDB else { return nil }
        let exponent = (db - referenceDB) / exchangeRate
        return referenceSeconds / pow(2.0, exponent)
    }

    /// Human-readable, localized exposure guidance for a sustained level.
    static func guidance(forDB db: Double) -> LocalizedStringKey {
        guard let seconds = permissibleSeconds(forDB: db) else {
            return "exposure.safe"
        }
        if seconds >= 3600 {
            let hours = Int((seconds / 3600).rounded())
            return "exposure.limitHours \(hours)"
        } else if seconds >= 60 {
            let minutes = max(1, Int((seconds / 60).rounded()))
            return "exposure.limitMinutes \(minutes)"
        } else {
            let secs = max(1, Int(seconds.rounded()))
            return "exposure.limitSeconds \(secs)"
        }
    }
}
