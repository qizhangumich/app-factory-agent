import SwiftUI

/// Equal / Unequal split toggle (spec component "Equal/Unequal split toggle").
struct SplitModeToggle: View {

    @Binding var isUnequalSplit: Bool

    var body: some View {
        Picker("Split mode", selection: $isUnequalSplit) {
            Text("Equal Split").tag(false)
            Text("Unequal Split").tag(true)
        }
        .pickerStyle(.segmented)
        .onChange(of: isUnequalSplit) { _ in Haptics.selection() }
        .accessibilityLabel("Split mode")
        .accessibilityValue(isUnequalSplit ? "Unequal split" : "Equal split")
    }
}
