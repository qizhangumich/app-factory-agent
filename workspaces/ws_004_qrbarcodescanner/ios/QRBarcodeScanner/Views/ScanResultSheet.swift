//
//  ScanResultSheet.swift
//  QRBarcodeScanner
//
//  The bottom sheet shown over the camera when a code is detected.
//

import SwiftUI

/// Bottom-sheet content presenting the most recent scan with actions.
struct ScanResultSheet: View {

    let result: ScanResult
    /// Called when the user dismisses the sheet to resume scanning.
    var onScanAgain: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            HStack {
                Text("Scan Result")
                    .font(.headline)
                Spacer()
                Text(DateFormatting.scanTimestamp.string(from: result.timestamp))
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            ResultActionsView(result: result)

            Button {
                HapticEngine.tick()
                onScanAgain()
            } label: {
                Label("Scan Again", systemImage: "viewfinder")
                    .frame(maxWidth: .infinity)
                    .font(.subheadline.weight(.semibold))
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
            .tint(.scanSuccess)
            .accessibilityHint("Dismisses this result and resumes scanning")
        }
        .padding(20)
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
        .modifier(MaterialSheetBackground())
    }
}

/// Applies a translucent material sheet background on iOS 16.4+, where the
/// `presentationBackground` modifier is available; a no-op on 16.0–16.3.
private struct MaterialSheetBackground: ViewModifier {
    func body(content: Content) -> some View {
        if #available(iOS 16.4, *) {
            content.presentationBackground(.regularMaterial)
        } else {
            content
        }
    }
}
