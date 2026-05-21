//
//  ScannerController.swift
//  QRBarcodeScanner
//
//  Observable controller wrapping an AVCaptureSession + AVCaptureMetadataOutput.
//  Owns camera permission state, the torch (flashlight), and emits decoded
//  codes to SwiftUI. The actual preview is rendered by CameraPreviewView
//  (a UIViewControllerRepresentable) which displays this controller's session.
//

import AVFoundation
import Combine
import UIKit

/// Camera permission states surfaced to the UI.
enum CameraAuthState {
    case unknown
    case authorized
    case denied
}

/// Drives the live camera scanning pipeline.
@MainActor
final class ScannerController: NSObject, ObservableObject {

    /// The capture session displayed by the preview layer.
    let session = AVCaptureSession()

    /// Current camera authorization state.
    @Published var authState: CameraAuthState = .unknown

    /// Whether the torch is currently on.
    @Published var isTorchOn: Bool = false

    /// True when the active device has a torch available.
    @Published var hasTorch: Bool = false

    /// Set briefly to flash a green confirmation overlay after a scan.
    @Published var didFlashSuccess: Bool = false

    /// Called on the main actor when a new code is decoded.
    var onScan: ((ScanResult) -> Void)?

    private let metadataOutput = AVCaptureMetadataOutput()
    private let sessionQueue = DispatchQueue(label: "qrbarcodescanner.session")
    private var captureDevice: AVCaptureDevice?
    private var isConfigured = false

    /// Throttles repeated detections of the same code while it stays in frame.
    private var lastValue: String?
    private var lastScanAt: Date = .distantPast
    private let dedupeInterval: TimeInterval = 2.0

    // MARK: - Permissions

    /// Requests camera access and configures the session when granted.
    func requestAccessAndConfigure() {
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized:
            authState = .authorized
            configureSession()
        case .notDetermined:
            AVCaptureDevice.requestAccess(for: .video) { [weak self] granted in
                Task { @MainActor in
                    guard let self else { return }
                    self.authState = granted ? .authorized : .denied
                    if granted { self.configureSession() }
                }
            }
        default:
            authState = .denied
        }
    }

    // MARK: - Session lifecycle

    /// Builds the capture graph: back camera input -> metadata output.
    private func configureSession() {
        guard !isConfigured else {
            start()
            return
        }
        sessionQueue.async { [weak self] in
            guard let self else { return }
            self.session.beginConfiguration()
            self.session.sessionPreset = .high

            guard
                let device = AVCaptureDevice.default(.builtInWideAngleCamera,
                                                     for: .video,
                                                     position: .back),
                let input = try? AVCaptureDeviceInput(device: device),
                self.session.canAddInput(input)
            else {
                self.session.commitConfiguration()
                return
            }
            self.session.addInput(input)
            self.captureDevice = device

            if self.session.canAddOutput(self.metadataOutput) {
                self.session.addOutput(self.metadataOutput)
                self.metadataOutput.setMetadataObjectsDelegate(
                    self, queue: DispatchQueue.main)
                // Only request types actually supported by the hardware.
                let available = self.metadataOutput.availableMetadataObjectTypes
                let wanted = BarcodeSymbology.supportedTypes.filter {
                    available.contains($0)
                }
                self.metadataOutput.metadataObjectTypes = wanted
            }

            self.session.commitConfiguration()
            self.isConfigured = true

            let torchAvailable = device.hasTorch && device.isTorchAvailable
            Task { @MainActor in
                self.hasTorch = torchAvailable
            }
            self.session.startRunning()
        }
    }

    /// Starts the session if it is configured and not already running.
    func start() {
        guard isConfigured else { return }
        sessionQueue.async { [weak self] in
            guard let self, !self.session.isRunning else { return }
            self.session.startRunning()
        }
    }

    /// Stops the session (e.g. when leaving the scanner screen).
    func stop() {
        sessionQueue.async { [weak self] in
            guard let self, self.session.isRunning else { return }
            self.session.stopRunning()
        }
    }

    // MARK: - Torch

    /// Toggles the flashlight on the active capture device.
    func toggleTorch() {
        guard let device = captureDevice, device.hasTorch,
              device.isTorchAvailable else { return }
        do {
            try device.lockForConfiguration()
            if device.torchMode == .on {
                device.torchMode = .off
                isTorchOn = false
            } else {
                try device.setTorchModeOn(level: 1.0)
                isTorchOn = true
            }
            device.unlockForConfiguration()
        } catch {
            // Torch unavailable (e.g. overheating); leave state unchanged.
        }
    }

    /// Ensures the torch is off (called when the session is torn down).
    func turnTorchOff() {
        guard let device = captureDevice, device.hasTorch,
              device.torchMode == .on else { return }
        try? device.lockForConfiguration()
        device.torchMode = .off
        device.unlockForConfiguration()
        isTorchOn = false
    }
}

// MARK: - AVCaptureMetadataOutputObjectsDelegate

extension ScannerController: AVCaptureMetadataOutputObjectsDelegate {

    nonisolated func metadataOutput(
        _ output: AVCaptureMetadataOutput,
        didOutput metadataObjects: [AVMetadataObject],
        from connection: AVCaptureConnection
    ) {
        // Delegate queue is main (configured above), but hop explicitly
        // to satisfy actor isolation.
        Task { @MainActor in
            self.handle(metadataObjects)
        }
    }

    private func handle(_ objects: [AVMetadataObject]) {
        guard
            let object = objects.first as? AVMetadataMachineReadableCodeObject,
            let value = object.stringValue,
            !value.isEmpty
        else { return }

        // Suppress duplicate emissions while a code lingers in frame.
        let now = Date()
        if value == lastValue, now.timeIntervalSince(lastScanAt) < dedupeInterval {
            return
        }
        lastValue = value
        lastScanAt = now

        let symbology = BarcodeSymbology.displayName(for: object.type,
                                                     value: value)
        let result = ScanResult(value: value, symbology: symbology)

        // Feedback: haptic + green success flash.
        HapticEngine.success()
        flashSuccess()
        onScan?(result)
    }

    /// Briefly raises the green success-flash flag.
    private func flashSuccess() {
        didFlashSuccess = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) { [weak self] in
            self?.didFlashSuccess = false
        }
    }
}
