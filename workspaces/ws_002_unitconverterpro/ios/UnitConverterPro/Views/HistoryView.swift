import SwiftUI

/// Screen 3: chronological list of past conversions. Tap to re-open, swipe to
/// delete, clear-all in the toolbar.
struct HistoryView: View {
    @EnvironmentObject private var store: AppStore
    @State private var showClearConfirm = false

    var body: some View {
        Group {
            if store.history.isEmpty {
                emptyState
            } else {
                historyList
            }
        }
        .navigationTitle(L.string("tab_history"))
        .toolbar {
            if !store.history.isEmpty {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(role: .destructive) {
                        showClearConfirm = true
                    } label: {
                        Text(L.string("action_clear_all"))
                    }
                }
            }
        }
        .confirmationDialog(L.string("confirm_clear_title"),
                            isPresented: $showClearConfirm,
                            titleVisibility: .visible) {
            Button(L.string("action_clear_all"), role: .destructive) {
                store.clearHistory()
            }
            Button(L.string("action_cancel"), role: .cancel) {}
        }
    }

    // MARK: - List

    private var historyList: some View {
        List {
            ForEach(store.history) { entry in
                if let row = HistoryRowData(entry: entry) {
                    NavigationLink {
                        ConversionView(category: row.category,
                                       initialFromID: row.from.id,
                                       initialToID: row.to.id,
                                       initialValue: row.inputPlain)
                    } label: {
                        HistoryRow(data: row)
                    }
                }
            }
            .onDelete { store.deleteHistory(at: $0) }
        }
        .listStyle(.insetGrouped)
    }

    // MARK: - Empty state

    private var emptyState: some View {
        // ContentUnavailableView requires iOS 17. The project deployment
        // target is iOS 16, so use a hand-rolled equivalent.
        VStack(spacing: 12) {
            Image(systemName: "clock.arrow.circlepath")
                .font(.system(size: 48))
                .foregroundStyle(.secondary)
            Text(L.string("history_empty_title"))
                .font(.title3)
                .fontWeight(.semibold)
            Text(L.string("history_empty_message"))
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

/// Resolved, display-ready data for a single history entry.
struct HistoryRowData {
    let entry: HistoryEntry
    let category: UnitCategory
    let from: ConvUnit
    let to: ConvUnit

    init?(entry: HistoryEntry) {
        guard let category = UnitData.category(withID: entry.categoryID),
              let from = category.unit(withID: entry.fromUnitID),
              let to = category.unit(withID: entry.toUnitID) else { return nil }
        self.entry = entry
        self.category = category
        self.from = from
        self.to = to
    }

    var inputDisplay: String { ConversionEngine.format(entry.inputValue) }
    var resultDisplay: String { ConversionEngine.format(entry.resultValue) }

    /// Plain (no grouping separators) input string for re-opening the converter.
    var inputPlain: String {
        inputDisplay.replacingOccurrences(of: ",", with: "")
    }

    var timestampDisplay: String {
        let f = DateFormatter()
        f.dateStyle = .short
        f.timeStyle = .short
        f.locale = Locale.current
        return f.string(from: entry.timestamp)
    }
}

/// One row in the history list.
struct HistoryRow: View {
    let data: HistoryRowData

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack(spacing: 6) {
                Image(systemName: data.category.systemImage)
                    .font(.caption)
                    .foregroundStyle(.indigo)
                Text(data.category.localizedName)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.secondary)
                Spacer()
                Text(data.timestampDisplay)
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }

            HStack(spacing: 6) {
                Text("\(data.inputDisplay) \(data.from.symbol)")
                    .font(.body.weight(.semibold))
                Image(systemName: "arrow.right")
                    .font(.caption)
                    .foregroundStyle(.orange)
                Text("\(data.resultDisplay) \(data.to.symbol)")
                    .font(.body.weight(.semibold))
                    .foregroundStyle(.indigo)
            }
        }
        .padding(.vertical, 4)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(Text(String(format: L.string("a11y_history_row"),
                                         data.inputDisplay, data.from.localizedName,
                                         data.resultDisplay, data.to.localizedName)))
    }
}
