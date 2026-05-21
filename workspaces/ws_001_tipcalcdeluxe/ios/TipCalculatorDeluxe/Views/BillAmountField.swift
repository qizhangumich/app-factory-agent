import SwiftUI

/// Bill amount input — numeric keyboard, auto-focus on launch (spec component).
struct BillAmountField: View {

    @Binding var text: String
    var isFocused: FocusState<Bool>.Binding

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Bill Amount")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.secondary)

            HStack(spacing: 8) {
                Text(CurrencyFormatter.symbol)
                    .font(.system(size: 34, weight: .bold, design: .rounded))
                    .foregroundStyle(.secondary)
                    .accessibilityHidden(true)

                TextField("0.00", text: $text)
                    .font(.system(size: 40, weight: .bold, design: .rounded))
                    .keyboardType(.decimalPad)
                    .focused(isFocused)
                    .accessibilityLabel("Bill amount in \(CurrencyFormatter.symbol)")
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(Color(.secondarySystemGroupedBackground))
        )
    }
}
