//
//  HistoryView.swift
//  QRBarcodeScanner
//
//  List of past scans with search, tap-to-detail, swipe-to-delete,
//  and a clear-all action.
//

import SwiftUI

struct HistoryView: View {

    @EnvironmentObject private var historyStore: HistoryStore
    @Environment(\.dismiss) private var dismiss

    @State private var searchText = ""
    @State private var showClearConfirm = false

    private var results: [ScanResult] {
        historyStore.filtered(by: searchText)
    }

    var body: some View {
        Group {
            if historyStore.scans.isEmpty {
                emptyState
            } else {
                listContent
            }
        }
        .navigationTitle("History")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                Button("Done") { dismiss() }
            }
            ToolbarItem(placement: .topBarTrailing) {
                Button(role: .destructive) {
                    showClearConfirm = true
                } label: {
                    Image(systemName: "trash")
                }
                .disabled(historyStore.scans.isEmpty)
                .accessibilityLabel("Clear all history")
            }
        }
        .confirmationDialog("Clear all scan history?",
                            isPresented: $showClearConfirm,
                            titleVisibility: .visible) {
            Button("Delete All Scans", role: .destructive) {
                HapticEngine.tick()
                historyStore.clearAll()
            }
            Button("Cancel", role: .cancel) { }
        } message: {
            Text("This permanently removes all "
                 + "\(historyStore.scans.count) saved scans from this device.")
        }
    }

    // MARK: - List

    private var listContent: some View {
        List {
            if results.isEmpty {
                ContentUnavailableViewCompat(
                    title: "No Matches",
                    systemImage: "magnifyingglass",
                    message: "No scans match \u{201C}\(searchText)\u{201D}.")
            } else {
                ForEach(results) { result in
                    NavigationLink {
                        ScanDetailView(result: result)
                    } label: {
                        HistoryRow(result: result)
                    }
                    .swipeActions(edge: .trailing) {
                        Button(role: .destructive) {
                            HapticEngine.tick()
                            historyStore.delete(result)
                        } label: {
                            Label("Delete", systemImage: "trash")
                        }
                    }
                }
            }
        }
        .listStyle(.plain)
        .searchable(text: $searchText,
                    placement: .navigationBarDrawer(displayMode: .always),
                    prompt: "Search scans")
    }

    private var emptyState: some View {
        ContentUnavailableViewCompat(
            title: "No Scans Yet",
            systemImage: "qrcode.viewfinder",
            message: "Codes you scan will appear here, "
                + "saved privately on this device.")
    }
}

/// A single row in the history list: type icon, content preview, timestamp.
private struct HistoryRow: View {
    let result: ScanResult

    var body: some View {
        HStack(spacing: 14) {
            Image(systemName: result.contentType.systemImage)
                .font(.system(size: 18, weight: .semibold))
                .foregroundStyle(.white)
                .frame(width: 40, height: 40)
                .background(Color.appPrimary, in: RoundedRectangle(cornerRadius: 10))

            VStack(alignment: .leading, spacing: 3) {
                Text(result.preview)
                    .font(.subheadline.weight(.medium))
                    .lineLimit(1)
                HStack(spacing: 6) {
                    Text(result.symbology)
                    Text("·")
                    Text(DateFormatting.relative.localizedString(
                        for: result.timestamp, relativeTo: Date()))
                }
                .font(.caption)
                .foregroundStyle(.secondary)
            }
        }
        .padding(.vertical, 4)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(result.contentType.displayName), "
                            + "\(result.preview)")
        .accessibilityHint("Opens full scan details")
    }
}

/// iOS 16-compatible stand-in for `ContentUnavailableView` (iOS 17+).
struct ContentUnavailableViewCompat: View {
    let title: String
    let systemImage: String
    let message: String

    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: systemImage)
                .font(.system(size: 52))
                .foregroundStyle(.secondary)
            Text(title)
                .font(.title3.weight(.semibold))
            Text(message)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .listRowSeparator(.hidden)
    }
}

#Preview {
    NavigationStack {
        HistoryView()
            .environmentObject(HistoryStore())
    }
}
