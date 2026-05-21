import SwiftUI

/// The single screen of the app (spec.ui_spec screen "MainCalculator").
struct MainCalculatorView: View {

    @StateObject private var viewModel = CalculatorViewModel()
    @StateObject private var history = HistoryStore()

    @State private var showingHistory = false
    @FocusState private var billFieldFocused: Bool

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 18) {
                    BillAmountField(
                        text: $viewModel.billText,
                        isFocused: $billFieldFocused
                    )

                    TipSliderView(
                        tipPercent: $viewModel.tipPercent,
                        tipAmount: viewModel.tipAmount,
                        range: viewModel.minTip...viewModel.maxTip
                    )

                    TaxControlView(
                        taxEnabled: $viewModel.taxEnabled,
                        taxText: $viewModel.taxText,
                        taxAmount: viewModel.taxAmount
                    )

                    PeopleStepperView(viewModel: viewModel)

                    SplitModeToggle(isUnequalSplit: $viewModel.isUnequalSplit)

                    if viewModel.isUnequalSplit && viewModel.people > 1 {
                        UnequalSplitEditor(viewModel: viewModel)
                    }

                    RoundingControlView(rounding: $viewModel.rounding)

                    ResultCardView(viewModel: viewModel)

                    SaveButton(viewModel: viewModel, history: history)
                }
                .padding()
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Tip Calculator")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button {
                        viewModel.reset()
                        billFieldFocused = true
                    } label: {
                        Image(systemName: "arrow.counterclockwise")
                    }
                    .accessibilityLabel("Reset calculator")
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        Haptics.light()
                        showingHistory = true
                    } label: {
                        Image(systemName: "clock.arrow.circlepath")
                    }
                    .accessibilityLabel("Calculation history")
                }
                ToolbarItemGroup(placement: .keyboard) {
                    Spacer()
                    Button("Done") { billFieldFocused = false }
                        .accessibilityLabel("Dismiss keyboard")
                }
            }
            .sheet(isPresented: $showingHistory) {
                HistoryView(history: history) { entry in
                    viewModel.restore(from: entry)
                    showingHistory = false
                }
            }
        }
        .onAppear {
            viewModel.syncWeights()
            // Auto-focus the bill field on launch (spec component).
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) {
                billFieldFocused = true
            }
        }
    }
}

#Preview {
    MainCalculatorView()
}
