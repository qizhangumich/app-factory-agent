import Foundation
import Combine

/// Observable store that owns favorites and history, persisted to `UserDefaults`.
///
/// History is capped at the most recent 100 entries. All mutations publish
/// changes so SwiftUI views update automatically.
final class AppStore: ObservableObject {

    static let historyLimit = 100

    @Published private(set) var favorites: [FavoritePair] = []
    @Published private(set) var history: [HistoryEntry] = []

    private let defaults: UserDefaults
    private let favoritesKey = "ucp.favorites.v1"
    private let historyKey = "ucp.history.v1"

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
        load()
    }

    // MARK: - Loading / Saving

    private func load() {
        let decoder = JSONDecoder()
        if let data = defaults.data(forKey: favoritesKey),
           let decoded = try? decoder.decode([FavoritePair].self, from: data) {
            favorites = decoded
        }
        if let data = defaults.data(forKey: historyKey),
           let decoded = try? decoder.decode([HistoryEntry].self, from: data) {
            history = decoded
        }
    }

    private func saveFavorites() {
        if let data = try? JSONEncoder().encode(favorites) {
            defaults.set(data, forKey: favoritesKey)
        }
    }

    private func saveHistory() {
        if let data = try? JSONEncoder().encode(history) {
            defaults.set(data, forKey: historyKey)
        }
    }

    // MARK: - Favorites

    func isFavorite(categoryID: String, fromUnitID: String, toUnitID: String) -> Bool {
        favorites.contains {
            $0.categoryID == categoryID &&
            $0.fromUnitID == fromUnitID &&
            $0.toUnitID == toUnitID
        }
    }

    func toggleFavorite(categoryID: String, fromUnitID: String, toUnitID: String) {
        let pair = FavoritePair(categoryID: categoryID,
                                fromUnitID: fromUnitID,
                                toUnitID: toUnitID)
        if let idx = favorites.firstIndex(where: { $0.id == pair.id }) {
            favorites.remove(at: idx)
        } else {
            favorites.insert(pair, at: 0)
        }
        saveFavorites()
    }

    func removeFavorite(_ pair: FavoritePair) {
        favorites.removeAll { $0.id == pair.id }
        saveFavorites()
    }

    // MARK: - History

    /// Records a conversion. No-ops on invalid input so history stays clean.
    func addHistory(categoryID: String,
                    fromUnitID: String,
                    toUnitID: String,
                    inputValue: Double,
                    resultValue: Double) {
        guard inputValue.isFinite, resultValue.isFinite else { return }
        let entry = HistoryEntry(categoryID: categoryID,
                                 fromUnitID: fromUnitID,
                                 toUnitID: toUnitID,
                                 inputValue: inputValue,
                                 resultValue: resultValue)
        history.insert(entry, at: 0)
        if history.count > Self.historyLimit {
            history = Array(history.prefix(Self.historyLimit))
        }
        saveHistory()
    }

    func deleteHistory(_ entry: HistoryEntry) {
        history.removeAll { $0.id == entry.id }
        saveHistory()
    }

    func deleteHistory(at offsets: IndexSet) {
        history.remove(atOffsets: offsets)
        saveHistory()
    }

    func clearHistory() {
        history.removeAll()
        saveHistory()
    }
}
