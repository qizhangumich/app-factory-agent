import Foundation

/// A single dB measurement captured during a session, used by the chart.
struct SessionSample: Identifiable, Equatable {
    let id = UUID()
    /// Seconds elapsed since the session started.
    let elapsed: TimeInterval
    /// Measured sound level in dB.
    let db: Double
}
