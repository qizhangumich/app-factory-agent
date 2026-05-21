//
//  BarcodeSymbology.swift
//  QRBarcodeScanner
//
//  Maps AVFoundation metadata object types to the symbologies declared
//  in the app spec, and provides the full set of types the scanner
//  listens for.
//

import AVFoundation

enum BarcodeSymbology {

    /// Every metadata object type the scanner should detect.
    /// Covers QR plus all 1D/2D barcodes listed in the app spec:
    /// EAN-13, EAN-8, UPC-A (derived from EAN-13), UPC-E, Code 128,
    /// Code 39, ITF, PDF417, Aztec, Data Matrix.
    static let supportedTypes: [AVMetadataObject.ObjectType] = [
        .qr,
        .ean13,
        .ean8,
        .upce,
        .code128,
        .code39,
        .code39Mod43,
        .code93,
        .interleaved2of5,   // ITF
        .itf14,
        .pdf417,
        .aztec,
        .dataMatrix
    ]

    /// Human-readable name for a detected metadata object type.
    ///
    /// EAN-13 payloads beginning with `0` are actually UPC-A codes;
    /// callers may pass the decoded value to refine the label.
    static func displayName(for type: AVMetadataObject.ObjectType,
                            value: String? = nil) -> String {
        switch type {
        case .qr:
            return "QR Code"
        case .ean13:
            if let v = value, v.count == 13, v.hasPrefix("0") {
                return "UPC-A"
            }
            return "EAN-13"
        case .ean8:
            return "EAN-8"
        case .upce:
            return "UPC-E"
        case .code128:
            return "Code 128"
        case .code39, .code39Mod43:
            return "Code 39"
        case .code93:
            return "Code 93"
        case .interleaved2of5:
            return "ITF"
        case .itf14:
            return "ITF-14"
        case .pdf417:
            return "PDF417"
        case .aztec:
            return "Aztec"
        case .dataMatrix:
            return "Data Matrix"
        default:
            return "Barcode"
        }
    }
}
