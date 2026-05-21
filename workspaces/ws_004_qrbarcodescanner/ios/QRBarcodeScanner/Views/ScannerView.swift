//
//  ScannerView.swift
//  QRBarcodeScanner
//
//  Primary screen: full-screen camera preview, scan-target overlay,
//  flashlight (top-right), history (top-left), photo import (bottom-left),
//  and a result bottom sheet on detection.
//

import SwiftUI

struct ScannerView: View {

    @EnvironmentObject private var historyStore: HistoryStore
    @StateObject private var scanner = ScannerController()
    @Environment(\.scenePhase) private var scenePhase

    @State private var currentResult: ScanResult?
    @State private var showHistory = false
    @State private var showPhotoPicker = false
    @State private var importError: String?

    var body: some View {
        ZStack {
            cameraLayer

            if scanner.authState == .authorized {
                ScanOverlayView(didFlashSuccess: scanner.didFlashSuccess)
                controlsLayer
            } else if scanner.authState == .denied {
                permissionDeniedLayer
            } else {
                Color.black.ignoresSafeArea()
                ProgressView()
                    .tint(.white)
            }
        }
        .statusBarHidden(false)
        .onAppear(perform: configureScanner)
        .onDisappear {
            scanner.turnTorchOff()
            scanner.stop()
        }
        .onChange(of: scenePhase) { phase in
            switch phase {
            case .active:
                if scanner.authState == .authorized && currentResult == nil {
                    scanner.start()
                }
            case .background, .inactive:
                scanner.turnTorchOff()
                scanner.stop()
            @unknown default:
                break
            }
        }
        .sheet(item: $currentResult, onDismiss: resumeScanning) { result in
            ScanResultSheet(result: result) {
                currentResult = nil
            }
        }
        .sheet(isPresented: $showHistory) {
            NavigationStack {
                HistoryView()
            }
        }
        .sheet(isPresented: $showPhotoPicker) {
            PhotoPicker(onPick: handlePickedImage)
                .ignoresSafeArea()
        }
        .alert("No Code Found",
               isPresented: Binding(get: { importError != nil },
                                    set: { if !$0 { importError = nil } })) {
            Button("OK", role: .cancel) { importError = nil }
        } message: {
            Text(importError ?? "")
        }
    }

    // MARK: - Layers

    private var cameraLayer: some View {
        Group {
            if scanner.authState == .authorized {
                CameraPreviewView(session: scanner.session)
                    .ignoresSafeArea()
            } else {
                Color.black.ignoresSafeArea()
            }
        }
    }

    private var controlsLayer: some View {
        VStack {
            HStack(alignment: .top) {
                circleButton(system: "clock.arrow.circlepath",
                             label: "Scan history") {
                    HapticEngine.tick()
                    showHistory = true
                }

                Spacer()

                if scanner.hasTorch {
                    circleButton(
                        system: scanner.isTorchOn
                            ? "bolt.fill" : "bolt.slash.fill",
                        label: scanner.isTorchOn
                            ? "Turn flashlight off" : "Turn flashlight on",
                        tinted: scanner.isTorchOn
                    ) {
                        scanner.toggleTorch()
                        HapticEngine.tick()
                    }
                }
            }

            Spacer()

            Text("Point the camera at a QR code or barcode")
                .font(.subheadline.weight(.medium))
                .foregroundStyle(.white)
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(.black.opacity(0.45), in: Capsule())
                .accessibilityHidden(true)

            HStack {
                circleButton(system: "photo.on.rectangle",
                             label: "Scan a code from a photo") {
                    HapticEngine.tick()
                    showPhotoPicker = true
                }
                Spacer()
            }
            .padding(.top, 14)
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 14)
    }

    private var permissionDeniedLayer: some View {
        VStack(spacing: 16) {
            Image(systemName: "camera.metering.none")
                .font(.system(size: 56))
                .foregroundStyle(.secondary)
            Text("Camera Access Needed")
                .font(.title2.weight(.bold))
            Text("QR & Barcode Scanner+ needs the camera to scan codes. "
                 + "Enable camera access in Settings to start scanning.")
                .font(.body)
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
                .padding(.horizontal, 32)
            Button("Open Settings") {
                if let url = URL(string: UIApplication.openSettingsURLString) {
                    UIApplication.shared.open(url)
                }
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)

            Button("Scan from Photo Library") {
                showPhotoPicker = true
            }
            .buttonStyle(.bordered)
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.black.ignoresSafeArea())
    }

    // MARK: - Building blocks

    private func circleButton(system: String,
                              label: String,
                              tinted: Bool = false,
                              action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Image(systemName: system)
                .font(.system(size: 20, weight: .semibold))
                .foregroundStyle(tinted ? Color.yellow : .white)
                .frame(width: 48, height: 48)
                .background(.black.opacity(0.5), in: Circle())
        }
        .accessibilityLabel(label)
    }

    // MARK: - Actions

    private func configureScanner() {
        scanner.onScan = { result in
            // Save to history and present the result sheet.
            historyStore.add(result)
            currentResult = result
            scanner.stop()
        }
        scanner.requestAccessAndConfigure()
    }

    private func resumeScanning() {
        // Sheet dismissed: clear the result and restart the live feed.
        currentResult = nil
        if scanner.authState == .authorized {
            scanner.start()
        }
    }

    private func handlePickedImage(_ image: UIImage?) {
        guard let image else { return }
        if let result = ImageScanner.decode(from: image) {
            historyStore.add(result)
            currentResult = result
            scanner.stop()
        } else {
            importError = "We couldn't find a QR code in that image. "
                + "Try a clearer photo."
        }
    }
}

#Preview {
    ScannerView()
        .environmentObject(HistoryStore())
}
