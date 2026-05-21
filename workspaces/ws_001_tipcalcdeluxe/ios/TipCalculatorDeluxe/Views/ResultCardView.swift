import SwiftUI

/// Result card — per-person total, tip and tax (spec component "Result card").
struct ResultCardView: View {

    @ObservedObject var viewModel: CalculatorViewModel

    var body: some View {
        VStack(spacing: 14) {
            // Headline: total per person.
            VStack(spacing: 2) {
                Text(viewModel.isUnequalSplit ? "Grand Total" : "Each Person Pays")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.white.opacity(0.85))
                Text(CurrencyFormatter.string(
                    from: viewModel.isUnequalSplit ? viewModel.grandTotal : viewModel.totalPerPerson
                ))
                .font(.system(size: 44, weight: .heavy, design: .rounded))
                .foregroundStyle(.white)
                .monospacedDigit()
                .contentTransition(.numericText())
                .minimumScaleFactor(0.5)
                .lineLimit(1)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 8)

            Divider().overlay(Color.white.opacity(0.3))

            // Breakdown rows.
            VStack(spacing: 8) {
                breakdownRow(label: "Bill",
                             value: viewModel.billAmount)
                breakdownRow(label: "Tip (\(Int(viewModel.tipPercent.rounded()))%)",
                             value: viewModel.tipAmount)
                if viewModel.taxEnabled {
                    breakdownRow(label: "Tax",
                                 value: viewModel.taxAmount)
                }
                breakdownRow(label: "Grand Total",
                             value: viewModel.grandTotal,
                             emphasized: true)
            }

            if !viewModel.isUnequalSplit {
                Divider().overlay(Color.white.opacity(0.3))
                VStack(spacing: 8) {
                    breakdownRow(label: "Tip per Person",
                                 value: viewModel.tipPerPerson)
                    if viewModel.taxEnabled {
                        breakdownRow(label: "Tax per Person",
                                     value: viewModel.taxPerPerson)
                    }
                    breakdownRow(label: "Total per Person",
                                 value: viewModel.totalPerPerson,
                                 emphasized: true)
                }
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .fill(
                    LinearGradient(
                        colors: [Color.blue, Color.blue.opacity(0.78)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
        )
        .opacity(viewModel.hasBill ? 1 : 0.55)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(accessibilitySummary)
    }

    @ViewBuilder
    private func breakdownRow(label: String, value: Double, emphasized: Bool = false) -> some View {
        HStack {
            Text(label)
                .font(emphasized ? .subheadline.weight(.bold) : .subheadline)
                .foregroundStyle(.white.opacity(emphasized ? 1 : 0.85))
            Spacer()
            Text(CurrencyFormatter.string(from: value))
                .font(emphasized ? .subheadline.weight(.bold) : .subheadline.weight(.medium))
                .foregroundStyle(.white)
                .monospacedDigit()
        }
    }

    private var accessibilitySummary: String {
        if viewModel.isUnequalSplit {
            return "Grand total \(CurrencyFormatter.string(from: viewModel.grandTotal)), split unequally between \(viewModel.people) people."
        }
        return "Each of \(viewModel.people) people pays \(CurrencyFormatter.string(from: viewModel.totalPerPerson)), including \(CurrencyFormatter.string(from: viewModel.tipPerPerson)) tip."
    }
}
