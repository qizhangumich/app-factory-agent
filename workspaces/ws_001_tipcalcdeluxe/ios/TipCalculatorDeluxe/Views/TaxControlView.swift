import SwiftUI

/// Tax toggle + configurable rate field — default off (spec component).
struct TaxControlView: View {

    @Binding var taxEnabled: Bool
    @Binding var taxText: String
    let taxAmount: Double

    @FocusState private var rateFocused: Bool

    var body: some View {
        VStack(spacing: 12) {
            Toggle(isOn: $taxEnabled) {
                HStack {
                    Text("Add Tax")
                        .font(.subheadline.weight(.semibold))
                    if taxEnabled {
                        Spacer()
                        Text(CurrencyFormatter.string(from: taxAmount))
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(.green)
                            .monospacedDigit()
                    }
                }
            }
            .tint(.blue)
            .onChange(of: taxEnabled) { _ in Haptics.selection() }
            .accessibilityLabel("Include tax in the total")

            if taxEnabled {
                HStack {
                    Text("Tax Rate")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                    Spacer()
                    TextField("0", text: $taxText)
                        .keyboardType(.decimalPad)
                        .multilineTextAlignment(.trailing)
                        .frame(width: 70)
                        .focused($rateFocused)
                        .font(.body.weight(.semibold))
                        .accessibilityLabel("Tax rate percentage")
                    Text("%")
                        .font(.body.weight(.semibold))
                        .foregroundStyle(.secondary)
                }
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(Color(.secondarySystemGroupedBackground))
        )
    }
}
