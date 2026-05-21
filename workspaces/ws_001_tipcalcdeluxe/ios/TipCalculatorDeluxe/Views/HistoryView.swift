import SwiftUI

/// History sheet — shows the last 20 calculations (spec component
/// "History button (opens sheet with last 20 calculations)").
struct HistoryView: View {

    @ObservedObject var history: HistoryStore
    /// Called when a row is tapped, so the calculator can restore it.
    var onSelect: (TipCalculation) -> Void

    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            Group {
                if history.entries.isEmpty {
                    emptyState
                } else {
                    list
                }
            }
            .navigationTitle("History")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Done") { dismiss() }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    if !history.entries.isEmpty {
                        Button(role: .destructive) {
                            Haptics.medium()
                            withAnimation { history.clear() }
                        } label: {
                            Text("Clear")
                        }
                        .accessibilityLabel("Clear all history")
                    }
                }
            }
        }
    }

    private var emptyState: some View {
        VStack(spacing: 12) {
            Image(systemName: "clock.badge.questionmark")
                .font(.system(size: 48))
                .foregroundStyle(.secondary)
            Text("No Calculations Yet")
                .font(.headline)
            Text("Saved calculations appear here. Your last 20 are kept.")
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(.systemGroupedBackground))
    }

    private var list: some View {
        List {
            ForEach(history.entries) { entry in
                Button {
                    onSelect(entry)
                } label: {
                    HistoryRow(entry: entry)
                }
                .buttonStyle(.plain)
            }
            .onDelete { offsets in
                Haptics.light()
                history.delete(at: offsets)
            }
        }
        .listStyle(.insetGrouped)
    }
}

/// One row in the history list.
private struct HistoryRow: View {

    let entry: TipCalculation

    private static let dateFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateStyle = .medium
        f.timeStyle = .short
        return f
    }()

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(CurrencyFormatter.string(from: entry.totalPerPerson))
                    .font(.headline.weight(.bold))
                    .foregroundStyle(.green)
                Text("\(CurrencyFormatter.string(from: entry.billAmount)) bill · \(Int(entry.tipPercent.rounded()))% tip · \(entry.people) \(entry.people == 1 ? "person" : "people")")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text(Self.dateFormatter.string(from: entry.date))
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }
            Spacer()
            Image(systemName: "arrow.uturn.left.circle")
                .foregroundStyle(.blue)
        }
        .padding(.vertical, 4)
        .contentShape(Rectangle())
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(CurrencyFormatter.string(from: entry.totalPerPerson)) per person. Tap to restore.")
    }
}
