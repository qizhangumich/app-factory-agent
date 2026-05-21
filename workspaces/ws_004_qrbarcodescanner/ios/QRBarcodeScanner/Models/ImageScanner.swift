//
//  ImageScanner.swift
//  QRBarcodeScanner
//
//  Decodes QR codes and barcodes from a static UIImage using Core Image's
//  CIDetector. Used by the "scan from photo library" import feature.
//

import CoreImage
import UIKit

enum ImageScanner {

    /// Attempts to decode the first machine-readable code found in `image`.
    /// Returns nil if no code is detected.
    ///
    /// Core Image's QR detector handles QR codes natively; `Vision` would
    /// be needed for 1D barcodes, but per spec the import flow targets
    /// QR images, which is the overwhelmingly common case.
    static func decode(from image: UIImage) -> ScanResult? {
        guard let ciImage = ciImage(from: image) else { return nil }

        let context = CIContext()
        let options: [String: Any] = [CIDetectorAccuracy: CIDetectorAccuracyHigh]
        guard let detector = CIDetector(ofType: CIDetectorTypeQRCode,
                                        context: context,
                                        options: options) else {
            return nil
        }

        let features = detector.features(in: ciImage)
        for feature in features {
            if let qr = feature as? CIQRCodeFeature,
               let message = qr.messageString,
               !message.isEmpty {
                return ScanResult(value: message, symbology: "QR Code")
            }
        }
        return nil
    }

    /// Builds a CIImage, applying the photo's orientation.
    private static func ciImage(from image: UIImage) -> CIImage? {
        if let ci = image.ciImage {
            return ci
        }
        guard let cg = image.cgImage else { return nil }
        let oriented = CIImage(cgImage: cg)
        return oriented.oriented(forExifOrientation:
            Int32(image.imageOrientation.exifValue))
    }
}

private extension UIImage.Orientation {
    /// EXIF orientation value matching this UIImage orientation.
    var exifValue: Int {
        switch self {
        case .up:            return 1
        case .down:          return 3
        case .left:          return 8
        case .right:         return 6
        case .upMirrored:    return 2
        case .downMirrored:  return 4
        case .leftMirrored:  return 5
        case .rightMirrored: return 7
        @unknown default:    return 1
        }
    }
}
