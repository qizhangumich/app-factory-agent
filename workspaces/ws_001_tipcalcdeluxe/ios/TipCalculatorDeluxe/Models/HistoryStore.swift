import Foundation

/// Persists the last 20 calculations to `UserDefaults` (spec.data_storage).
final class HistoryStore: ObservableObject {

    /// Maximum number of calculations retained.
    static let maxEntries = 20

    private let defaultsKey = "tipcalc.history.v1"
    private let defaults: UserDefaults

    @Published private(set) var entries: [TipCalculation] = []

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
        load()
    }

    /// Insert a new calculation at the front, trimming to `maxEntries`.
    func add(_ calculation: TipCalculation) {
        entries.insert(calculation, at: 0)
        if entries.count > Self.maxEntries {
            entries = Array(entries.prefix(Self.maxEntries))
        }
        save()
    }

    /// Remove a single entry.
    func delete(_ calculation: TipCalculation) {
        entries.removeAll { $0.id == calculation.id }
        save()
    }

    /// Remove entries at the given offsets (List swipe-to-delete).
    func delete(at offsets: IndexSet) {
        entries.remove(atOffsets: offsets)
        save()
    }

    /// Clear all history.
    func clear() {
        entries.removeAll()
        save()
    }

    // MARK: Persistence

    private func load() {
        guard let data = defaults.data(forKey: defaultsKey) else { return }
        if let decoded = try? JSONDecoder().decode([TipCalculation].self, from: data) {
            entries = decoded
        }
    }

    private func save() {
        if let data = try? JSONEncoder().encode(entries) {
            defaults.set(data, forKey: defaultsKey)
        }
    }
}
