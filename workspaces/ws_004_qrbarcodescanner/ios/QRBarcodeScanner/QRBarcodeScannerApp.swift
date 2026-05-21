//
//  QRBarcodeScannerApp.swift
//  QRBarcodeScanner
//
//  Entry point for QR & Barcode Scanner+ — an ad-free, private,
//  on-device QR and barcode scanner.
//

import SwiftUI

@main
struct QRBarcodeScannerApp: App {
    /// Shared, app-wide store of past scans (persisted to UserDefaults).
    @StateObject private var historyStore = HistoryStore()

    var body: some Scene {
        WindowGroup {
            ScannerView()
                .environmentObject(historyStore)
                .preferredColorScheme(.dark)
        }
    }
}
