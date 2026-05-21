import SwiftUI

/// A sheet for adjusting the calibration offset (±10 dB), persisted via
/// `AudioMeter.calibrationOffset` (UserDefaults-backed).
struct CalibrationView: View {
    @ObservedObject var meter: AudioMeter
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Text("calibration.offset")
                            Spacer()
                            Text(offsetLabel)
                                .font(.system(.body, design: .rounded))
                                .fontWeight(.semibold)
                                .monospacedDigit()
                        }
                        Slider(value: $meter.calibrationOffset,
                               in: -10...10,
                               step: 0.5) {
                            Text("calibration.offset")
                        } minimumValueLabel: {
                            Text("-10")
                        } maximumValueLabel: {
                            Text("+10")
                        }
                        .accessibilityValue(Text(offsetLabel))

                        Button("calibration.reset") {
                            meter.calibrationOffset = 0
                        }
                        .font(.footnote)
                    }
                } header: {
                    Text("calibration.section")
                } footer: {
                    Text("calibration.help")
                }

                Section {
                    Text("disclaimer.body")
                        .font(.footnote)
                        .foregroundColor(.secondary)
                } header: {
                    Text("disclaimer.title")
                }
            }
            .navigationTitle(Text("calibration.title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("common.done") { dismiss() }
                }
            }
        }
    }

    private var offsetLabel: String {
        let v = meter.calibrationOffset
        return String(format: "%+.1f dB", v)
    }
}

#Preview {
    CalibrationView(meter: AudioMeter())
}
