import SwiftUI

/// Saves the current calculation to history with a brief confirmation.
struct SaveButton: View {

    @ObservedObject var viewModel: CalculatorViewModel
    @ObservedObject var history: HistoryStore

    @State private var justSaved = false

    var body: some View {
        Button {
            if viewModel.saveToHistory(history) {
                withAnimation { justSaved = true }
                DispatchQueue.main.asyncAfter(deadline: .now() + 1.6) {
                    withAnimation { justSaved = false }
                }
            }
        } label: {
            HStack {
                Image(systemName: justSaved ? "checkmark.circle.fill" : "square.and.arrow.down")
                Text(justSaved ? "Saved to History" : "Save Calculation")
                    .font(.headline)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .fill(justSaved ? Color.green : Color.blue)
            )
            .foregroundStyle(.white)
        }
        .disabled(!viewModel.hasBill)
        .opacity(viewModel.hasBill ? 1 : 0.5)
        .accessibilityLabel("Save this calculation to history")
        .accessibilityHint(viewModel.hasBill ? "" : "Enter a bill amount first")
    }
}
