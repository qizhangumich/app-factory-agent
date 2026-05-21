import SwiftUI

/// Number-of-people stepper — 1 to 20, default 2 (spec component).
struct PeopleStepperView: View {

    @ObservedObject var viewModel: CalculatorViewModel

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text("People")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.secondary)
                Text("\(viewModel.people)")
                    .font(.title2.weight(.bold))
                    .monospacedDigit()
                    .contentTransition(.numericText())
            }

            Spacer()

            HStack(spacing: 0) {
                stepperButton(
                    systemName: "minus",
                    enabled: viewModel.people > viewModel.minPeople,
                    action: viewModel.decrementPeople
                )
                .accessibilityLabel("Remove a person")

                Divider().frame(height: 28)

                stepperButton(
                    systemName: "plus",
                    enabled: viewModel.people < viewModel.maxPeople,
                    action: viewModel.incrementPeople
                )
                .accessibilityLabel("Add a person")
            }
            .background(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .fill(Color(.tertiarySystemGroupedBackground))
            )
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(Color(.secondarySystemGroupedBackground))
        )
        .accessibilityElement(children: .contain)
        .accessibilityValue("\(viewModel.people) people")
    }

    @ViewBuilder
    private func stepperButton(systemName: String, enabled: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Image(systemName: systemName)
                .font(.headline)
                .frame(width: 50, height: 44)
                .contentShape(Rectangle())
        }
        .disabled(!enabled)
        .foregroundStyle(enabled ? Color.blue : Color.secondary)
    }
}
