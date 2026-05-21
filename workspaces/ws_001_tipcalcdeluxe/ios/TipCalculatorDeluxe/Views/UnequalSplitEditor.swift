import SwiftUI

/// Editor for unequal splits — assigns a custom weight (share) per person
/// (spec feature "Unequal splits (assign custom amounts per person)").
struct UnequalSplitEditor: View {

    @ObservedObject var viewModel: CalculatorViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Shares per Person")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.secondary)

            Text("Set how much weight each person carries. Someone who ordered more gets a higher share.")
                .font(.caption)
                .foregroundStyle(.secondary)

            ForEach(0..<viewModel.people, id: \.self) { index in
                HStack {
                    Text("Person \(index + 1)")
                        .font(.subheadline.weight(.medium))

                    Spacer()

                    Stepper(
                        value: Binding(
                            get: { weight(at: index) },
                            set: { newValue in
                                viewModel.setWeight(newValue, at: index)
                                Haptics.light()
                            }
                        ),
                        in: 0...20,
                        step: 1
                    ) {
                        Text("\(Int(weight(at: index))) ×")
                            .font(.subheadline.weight(.semibold))
                            .monospacedDigit()
                    }
                    .labelsHidden()
                    .fixedSize()
                    .accessibilityLabel("Share for person \(index + 1)")
                    .accessibilityValue("\(Int(weight(at: index))) shares")

                    Text("\(Int(weight(at: index))) ×")
                        .font(.subheadline.weight(.semibold))
                        .monospacedDigit()
                        .frame(width: 44, alignment: .trailing)

                    Text(CurrencyFormatter.string(from: viewModel.unequalShare(for: index)))
                        .font(.subheadline.weight(.bold))
                        .foregroundStyle(.green)
                        .monospacedDigit()
                        .frame(width: 92, alignment: .trailing)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(Color(.secondarySystemGroupedBackground))
        )
        .onAppear { viewModel.syncWeights() }
    }

    private func weight(at index: Int) -> Double {
        guard index < viewModel.customWeights.count else { return 1 }
        return viewModel.customWeights[index]
    }
}
