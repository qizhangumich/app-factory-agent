//
//  ResultActionsView.swift
//  QRBarcodeScanner
//
//  Reusable presentation of a single ScanResult: type badge, content,
//  Wi-Fi / contact specifics, and open / copy / share action buttons.
//  Used by both the scanner bottom sheet and the history detail screen.
//

import SwiftUI
import UIKit

/// Renders a scan result and its actions. Adapts its open-button label
/// to the detected content type.
struct ResultActionsView: View {

    let result: ScanResult

    @State private var showShareSheet = false
    @State private var didCopy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            typeBadge

            contentBlock

            if let wifi = result.wifiCredentials {
                wifiDetails(wifi)
            }

            actionButtons
        }
        .sheet(isPresented: $showShareSheet) {
            ShareSheet(items: [result.value])
        }
    }

    // MARK: - Type badge

    private var typeBadge: some View {
        HStack(spacing: 6) {
            Image(systemName: result.contentType.systemImage)
            Text(result.contentType.displayName.uppercased())
                .font(.caption.weight(.bold))
            Text("·")
            Text(result.symbology)
                .font(.caption.weight(.semibold))
        }
        .foregroundStyle(.white)
        .padding(.horizontal, 12)
        .padding(.vertical, 6)
        .background(Color.appPrimary, in: Capsule())
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(result.contentType.displayName) "
                            + "from \(result.symbology)")
    }

    // MARK: - Content

    private var contentBlock: some View {
        ScrollView {
            Text(result.value)
                .font(.body.monospaced())
                .foregroundStyle(.primary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .textSelection(.enabled)
        }
        .frame(maxHeight: 160)
        .accessibilityLabel("Scanned content")
        .accessibilityValue(result.value)
    }

    private func wifiDetails(_ wifi: WiFiCredentials) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Label("Network: \(wifi.ssid)", systemImage: "wifi")
            if !wifi.password.isEmpty {
                Label("Password: \(wifi.password)", systemImage: "key.fill")
            }
            Label("Security: \(wifi.security)", systemImage: "lock.shield")
        }
        .font(.footnote)
        .foregroundStyle(.secondary)
    }

    // MARK: - Actions

    private var actionButtons: some View {
        HStack(spacing: 12) {
            if let url = result.openableURL {
                Button {
                    HapticEngine.tick()
                    UIApplication.shared.open(url)
                } label: {
                    Label(openLabel, systemImage: openIcon)
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .accessibilityLabel(openLabel)
            }

            Button {
                copyToClipboard()
            } label: {
                Label(didCopy ? "Copied" : "Copy",
                      systemImage: didCopy ? "checkmark" : "doc.on.doc")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.bordered)
            .accessibilityLabel("Copy content to clipboard")

            Button {
                HapticEngine.tick()
                showShareSheet = true
            } label: {
                Label("Share", systemImage: "square.and.arrow.up")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.bordered)
            .accessibilityLabel("Share content")
        }
        .font(.subheadline.weight(.semibold))
        .controlSize(.large)
    }

    private var openLabel: String {
        switch result.contentType {
        case .url:   return "Open Link"
        case .phone: return "Call"
        case .email: return "Email"
        case .sms:   return "Message"
        case .geo:   return "Map"
        default:     return "Open"
        }
    }

    private var openIcon: String {
        switch result.contentType {
        case .url:   return "safari"
        case .phone: return "phone.fill"
        case .email: return "envelope.fill"
        case .sms:   return "message.fill"
        case .geo:   return "map.fill"
        default:     return "arrow.up.right.square"
        }
    }

    private func copyToClipboard() {
        UIPasteboard.general.string = result.value
        HapticEngine.tick()
        withAnimation { didCopy = true }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.6) {
            withAnimation { didCopy = false }
        }
    }
}
