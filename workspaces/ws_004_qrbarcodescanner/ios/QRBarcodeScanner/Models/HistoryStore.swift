//
//  HistoryStore.swift
//  QRBarcodeScanner
//
//  Persists the scan history (most recent 200 entries) to UserDefaults.
//  All data stays on-device; nothing is transmitted.
//

import Foundation
import Combine

/// Observable store of past scans, backed by UserDefaults.
@MainActor
final class HistoryStore: ObservableObject {

    /// Maximum number of scans retained on device.
    static let maxEntries = 200

    private static let storageKey = "qrbarcodescanner.history.v1"

    /// All stored scans, newest first.
    @Published private(set) var scans: [ScanResult] = []

    private let defaults: UserDefaults

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
        load()
    }

    // MARK: - Mutations

    /// Records a new scan at the top of the history.
    ///
    /// If the most recent scan has the same value, it is treated as a
    /// duplicate and only its timestamp is refreshed (prevents the camera
    /// from flooding history while a code remains in frame).
    func add(_ result: ScanResult) {
        if let first = scans.first, first.value == result.value {
            scans[0] = result
        } else {
            scans.insert(result, at: 0)
        }
        if scans.count > Self.maxEntries {
            scans = Array(scans.prefix(Self.maxEntries))
        }
        save()
    }

    /// Removes a single scan.
    func delete(_ result: ScanResult) {
        scans.removeAll { $0.id == result.id }
        save()
    }

    /// Removes scans at the given offsets (used by `onDelete` in lists).
    func delete(atOffsets offsets: IndexSet) {
        scans.remove(atOffsets: offsets)
        save()
    }

    /// Clears the entire history.
    func clearAll() {
        scans.removeAll()
        save()
    }

    /// Returns scans matching a case-insensitive search query.
    func filtered(by query: String) -> [ScanResult] {
        let q = query.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !q.isEmpty else { return scans }
        return scans.filter {
            $0.value.localizedCaseInsensitiveContains(q) ||
            $0.symbology.localizedCaseInsensitiveContains(q) ||
            $0.contentType.displayName.localizedCaseInsensitiveContains(q)
        }
    }

    // MARK: - Persistence

    private func load() {
        guard let data = defaults.data(forKey: Self.storageKey) else { return }
        do {
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            scans = try decoder.decode([ScanResult].self, from: data)
        } catch {
            // Corrupt data: start clean rather than crash.
            scans = []
        }
    }

    private func save() {
        do {
            let encoder = JSONEncoder()
            encoder.dateEncodingStrategy = .iso8601
            let data = try encoder.encode(scans)
            defaults.set(data, forKey: Self.storageKey)
        } catch {
            // Persistence failure is non-fatal; in-memory state remains valid.
        }
    }
}
