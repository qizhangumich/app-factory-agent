//
//  ScanDetailView.swift
//  QRBarcodeScanner
//
//  Full detail screen for a single past scan, reachable from HistoryView.
//

import SwiftUI

struct ScanDetailView: View {

    let result: ScanResult

    @EnvironmentObject private var historyStore: HistoryStore
    @Environment(\.dismiss) private var dismiss
    @State private var showDeleteConfirm = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                HStack {
                    Image(systemName: result.contentType.systemImage)
                        .font(.system(size: 28, weight: .semibold))
                        .foregroundStyle(.white)
                        .frame(width: 56, height: 56)
                        .background(Color.appPrimary,
                                    in: RoundedRectangle(cornerRadius: 14))
                    VStack(alignment: .leading, spacing: 2) {
                        Text(result.contentType.displayName)
                            .font(.title3.weight(.bold))
                        Text("Scanned "
                             + DateFormatting.scanTimestamp.string(
                                from: result.timestamp))
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }

                Divider()

                ResultActionsView(result: result)
            }
            .padding(20)
        }
        .navigationTitle("Scan Detail")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button(role: .destructive) {
                    showDeleteConfirm = true
                } label: {
                    Image(systemName: "trash")
                }
                .accessibilityLabel("Delete this scan")
            }
        }
        .confirmationDialog("Delete this scan?",
                            isPresented: $showDeleteConfirm,
                            titleVisibility: .visible) {
            Button("Delete", role: .destructive) {
                HapticEngine.tick()
                historyStore.delete(result)
                dismiss()
            }
            Button("Cancel", role: .cancel) { }
        }
    }
}
