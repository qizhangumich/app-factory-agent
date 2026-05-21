//
//  PhotoPicker.swift
//  QRBarcodeScanner
//
//  PHPickerViewController bridge for importing an image from the photo
//  library to scan a QR code from it.
//

import PhotosUI
import SwiftUI

/// SwiftUI wrapper around PHPickerViewController for single-image selection.
struct PhotoPicker: UIViewControllerRepresentable {

    /// Called with the selected image, or nil if the user cancelled.
    var onPick: (UIImage?) -> Void

    func makeUIViewController(context: Context) -> PHPickerViewController {
        var config = PHPickerConfiguration()
        config.filter = .images
        config.selectionLimit = 1
        let picker = PHPickerViewController(configuration: config)
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ controller: PHPickerViewController,
                                context: Context) { }

    func makeCoordinator() -> Coordinator {
        Coordinator(onPick: onPick)
    }

    final class Coordinator: NSObject, PHPickerViewControllerDelegate {
        private let onPick: (UIImage?) -> Void

        init(onPick: @escaping (UIImage?) -> Void) {
            self.onPick = onPick
        }

        func picker(_ picker: PHPickerViewController,
                    didFinishPicking results: [PHPickerResult]) {
            picker.dismiss(animated: true)

            guard let provider = results.first?.itemProvider,
                  provider.canLoadObject(ofClass: UIImage.self) else {
                onPick(nil)
                return
            }
            provider.loadObject(ofClass: UIImage.self) { [onPick] object, _ in
                DispatchQueue.main.async {
                    onPick(object as? UIImage)
                }
            }
        }
    }
}
