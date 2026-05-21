import SwiftUI

/// Tip percentage slider — 0-50%, default 18%, shows the live dollar amount
/// (spec component "Tip percentage slider").
struct TipSliderView: View {

    @Binding var tipPercent: Double
    let tipAmount: Double
    let range: ClosedRange<Double>

    /// Common quick-pick percentages.
    private let presets: [Double] = [10, 15, 18, 20, 25]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("Tip")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.secondary)
                Spacer()
                Text("\(Int(tipPercent.rounded()))%")
                    .font(.headline.weight(.bold))
                    .foregroundStyle(.blue)
                Text(CurrencyFormatter.string(from: tipAmount))
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.green)
                    .monospacedDigit()
            }

            Slider(
                value: $tipPercent,
                in: range,
                step: 1
            ) {
                Text("Tip percentage")
            } minimumValueLabel: {
                Text("0%").font(.caption2).foregroundStyle(.secondary)
            } maximumValueLabel: {
                Text("50%").font(.caption2).foregroundStyle(.secondary)
            }
            .tint(.blue)
            .onChange(of: tipPercent) { _ in
                Haptics.light()
            }
            .accessibilityLabel("Tip percentage")
            .accessibilityValue("\(Int(tipPercent.rounded())) percent")

            HStack(spacing: 8) {
                ForEach(presets, id: \.self) { preset in
                    Button {
                        Haptics.selection()
                        tipPercent = preset
                    } label: {
                        Text("\(Int(preset))%")
                            .font(.footnote.weight(.semibold))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 8)
                            .background(
                                RoundedRectangle(cornerRadius: 10, style: .continuous)
                                    .fill(isSelected(preset)
                                          ? Color.blue
                                          : Color(.tertiarySystemGroupedBackground))
                            )
                            .foregroundStyle(isSelected(preset) ? .white : .primary)
                    }
                    .accessibilityLabel("Set tip to \(Int(preset)) percent")
                }
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(Color(.secondarySystemGroupedBackground))
        )
    }

    private func isSelected(_ preset: Double) -> Bool {
        Int(tipPercent.rounded()) == Int(preset)
    }
}
