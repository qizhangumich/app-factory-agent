//
//  CameraPreviewView.swift
//  QRBarcodeScanner
//
//  UIViewControllerRepresentable bridge that hosts an AVCaptureVideoPreviewLayer
//  filled with the ScannerController's session. This is the only AppKit/UIKit
//  bridge in the app; everything else is pure SwiftUI.
//

import AVFoundation
import SwiftUI
import UIKit

/// SwiftUI wrapper exposing the live camera feed.
struct CameraPreviewView: UIViewControllerRepresentable {

    /// The controller whose `session` is displayed.
    let session: AVCaptureSession

    func makeUIViewController(context: Context) -> PreviewViewController {
        let controller = PreviewViewController()
        controller.previewLayer.session = session
        return controller
    }

    func updateUIViewController(_ controller: PreviewViewController,
                                context: Context) {
        controller.previewLayer.session = session
    }
}

/// View controller whose backing layer is an AVCaptureVideoPreviewLayer.
final class PreviewViewController: UIViewController {

    /// Convenience accessor for the view's backing preview layer.
    var previewLayer: AVCaptureVideoPreviewLayer {
        // `view`'s layerClass is overridden below, so this cast is safe.
        view.layer as! AVCaptureVideoPreviewLayer
    }

    override func loadView() {
        view = PreviewBackingView()
        view.backgroundColor = .black
        previewLayer.videoGravity = .resizeAspectFill
    }
}

/// A UIView whose backing layer type is AVCaptureVideoPreviewLayer.
private final class PreviewBackingView: UIView {
    override class var layerClass: AnyClass {
        AVCaptureVideoPreviewLayer.self
    }
}
