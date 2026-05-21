import SwiftUI

/// Round up / down / exact segmented control (spec component).
struct RoundingControlView: View {

    @Binding var rounding: Rounding

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Rounding")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.secondary)

            Picker("Rounding", selection: $rounding) {
                ForEach(Rounding.allCases) { mode in
                    Text(mode.label).tag(mode)
                }
            }
            .pickerStyle(.segmented)
            .onChange(of: rounding) { _ in Haptics.selection() }
            .accessibilityLabel("Total rounding mode")
            .accessibilityValue(rounding.label)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(Color(.secondarySystemGroupedBackground))
        )
    }
}
