//
//  ScanResult.swift
//  QRBarcodeScanner
//
//  Model representing a single decoded code, plus auto-detection of
//  the content's semantic type (URL / WiFi / vCard / phone / email / text).
//

import Foundation

/// Semantic classification of decoded content.
enum ScanContentType: String, Codable, CaseIterable {
    case url
    case wifi
    case contact
    case phone
    case email
    case sms
    case geo
    case text

    /// SF Symbol used to represent the type in lists and badges.
    var systemImage: String {
        switch self {
        case .url:     return "link"
        case .wifi:    return "wifi"
        case .contact: return "person.crop.rectangle"
        case .phone:   return "phone"
        case .email:   return "envelope"
        case .sms:     return "message"
        case .geo:     return "mappin.and.ellipse"
        case .text:    return "text.alignleft"
        }
    }

    /// Short human-readable label for the type badge.
    var displayName: String {
        switch self {
        case .url:     return "Link"
        case .wifi:    return "Wi-Fi"
        case .contact: return "Contact"
        case .phone:   return "Phone"
        case .email:   return "Email"
        case .sms:     return "SMS"
        case .geo:     return "Location"
        case .text:    return "Text"
        }
    }
}

/// Parsed Wi-Fi network credentials from a `WIFI:` payload.
struct WiFiCredentials: Codable, Equatable {
    var ssid: String
    var password: String
    var security: String   // WPA / WEP / nopass
    var hidden: Bool
}

/// A single scan: the raw value, its detected symbology and content type,
/// and when it was captured.
struct ScanResult: Identifiable, Codable, Equatable {
    let id: UUID
    /// Raw string decoded from the code.
    let value: String
    /// Barcode symbology (e.g. "QR Code", "EAN-13"). Human readable.
    let symbology: String
    /// Detected semantic content type.
    let contentType: ScanContentType
    /// Capture timestamp.
    let timestamp: Date

    init(id: UUID = UUID(),
         value: String,
         symbology: String,
         timestamp: Date = Date()) {
        self.id = id
        self.value = value
        self.symbology = symbology
        self.timestamp = timestamp
        self.contentType = ScanResult.detectType(from: value)
    }

    /// A trimmed, single-line preview suitable for list rows.
    var preview: String {
        let collapsed = value
            .replacingOccurrences(of: "\n", with: " ")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        if collapsed.count > 90 {
            return String(collapsed.prefix(90)) + "…"
        }
        return collapsed
    }

    /// A URL when the content is openable, otherwise nil.
    var openableURL: URL? {
        switch contentType {
        case .url:
            return URL(string: value.trimmingCharacters(in: .whitespacesAndNewlines))
        case .phone:
            let digits = value.replacingOccurrences(of: "tel:", with: "",
                                                    options: .caseInsensitive)
            return URL(string: "tel:" + digits.trimmingCharacters(in: .whitespaces))
        case .email:
            let addr = value.replacingOccurrences(of: "mailto:", with: "",
                                                  options: .caseInsensitive)
            return URL(string: "mailto:" + addr.trimmingCharacters(in: .whitespaces))
        case .sms:
            return URL(string: value)
        case .geo:
            return URL(string: value)
        default:
            return nil
        }
    }

    /// Parsed Wi-Fi credentials, when the content is a Wi-Fi payload.
    var wifiCredentials: WiFiCredentials? {
        ScanResult.parseWiFi(from: value)
    }

    // MARK: - Detection

    /// Classifies a raw decoded string into a `ScanContentType`.
    static func detectType(from raw: String) -> ScanContentType {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        let lower = trimmed.lowercased()

        if lower.hasPrefix("wifi:") {
            return .wifi
        }
        if lower.hasPrefix("begin:vcard") || lower.hasPrefix("mecard:") {
            return .contact
        }
        if lower.hasPrefix("mailto:") {
            return .email
        }
        if lower.hasPrefix("tel:") {
            return .phone
        }
        if lower.hasPrefix("smsto:") || lower.hasPrefix("sms:") {
            return .sms
        }
        if lower.hasPrefix("geo:") {
            return .geo
        }
        if lower.hasPrefix("http://") || lower.hasPrefix("https://") {
            return .url
        }
        // Bare domain heuristic: "example.com", "www.site.org/path"
        if isLikelyBareURL(trimmed) {
            return .url
        }
        // Bare email heuristic.
        if isLikelyEmail(trimmed) {
            return .email
        }
        return .text
    }

    /// True when the string looks like a bare URL without a scheme.
    private static func isLikelyBareURL(_ s: String) -> Bool {
        guard !s.contains(" "), s.contains(".") else { return false }
        let host = s.split(separator: "/").first.map(String.init) ?? s
        let parts = host.split(separator: ".")
        guard parts.count >= 2, let tld = parts.last, tld.count >= 2 else {
            return false
        }
        return tld.allSatisfy { $0.isLetter }
    }

    /// True when the string looks like a bare email address.
    private static func isLikelyEmail(_ s: String) -> Bool {
        guard !s.contains(" "), s.contains("@"), s.contains(".") else {
            return false
        }
        let parts = s.split(separator: "@")
        return parts.count == 2 && parts[1].contains(".")
    }

    /// Parses a `WIFI:S:<ssid>;T:<type>;P:<password>;H:<hidden>;;` payload.
    static func parseWiFi(from raw: String) -> WiFiCredentials? {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard trimmed.lowercased().hasPrefix("wifi:") else { return nil }

        let body = String(trimmed.dropFirst(5))
        var ssid = "", password = "", security = "nopass", hidden = false

        // Fields are ';'-separated; values may contain escaped '\;' '\:' '\\'.
        var fields: [String] = []
        var current = ""
        var escaped = false
        for ch in body {
            if escaped {
                current.append(ch)
                escaped = false
            } else if ch == "\\" {
                escaped = true
            } else if ch == ";" {
                fields.append(current)
                current = ""
            } else {
                current.append(ch)
            }
        }
        if !current.isEmpty { fields.append(current) }

        for field in fields {
            guard let sep = field.firstIndex(of: ":") else { continue }
            let key = String(field[..<sep]).uppercased()
            let val = String(field[field.index(after: sep)...])
            switch key {
            case "S": ssid = val
            case "P": password = val
            case "T": security = val.isEmpty ? "nopass" : val
            case "H": hidden = (val.lowercased() == "true")
            default: break
            }
        }
        guard !ssid.isEmpty else { return nil }
        return WiFiCredentials(ssid: ssid,
                               password: password,
                               security: security,
                               hidden: hidden)
    }
}
