//
//  ShareSheet.swift
//  QRBarcodeScanner
//
//  UIActivityViewController bridge for the system share sheet.
//

import SwiftUI
import UIKit

/// SwiftUI wrapper around UIActivityViewController.
struct ShareSheet: UIViewControllerRepresentable {

    /// Items to share (typically a single scanned string).
    let items: [Any]

    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: items,
                                 applicationActivities: nil)
    }

    func updateUIViewController(_ controller: UIActivityViewController,
                                context: Context) { }
}
