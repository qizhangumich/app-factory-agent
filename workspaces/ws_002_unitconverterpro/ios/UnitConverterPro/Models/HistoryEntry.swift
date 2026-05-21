import Foundation

/// A completed conversion recorded in history.
struct HistoryEntry: Identifiable, Codable, Hashable {
    let id: UUID
    let categoryID: String
    let fromUnitID: String
    let toUnitID: String
    let inputValue: Double
    let resultValue: Double
    let timestamp: Date

    init(id: UUID = UUID(),
         categoryID: String,
         fromUnitID: String,
         toUnitID: String,
         inputValue: Double,
         resultValue: Double,
         timestamp: Date = Date()) {
        self.id = id
        self.categoryID = categoryID
        self.fromUnitID = fromUnitID
        self.toUnitID = toUnitID
        self.inputValue = inputValue
        self.resultValue = resultValue
        self.timestamp = timestamp
    }
}

/// A starred conversion pair for quick access.
struct FavoritePair: Identifiable, Codable, Hashable {
    let categoryID: String
    let fromUnitID: String
    let toUnitID: String

    /// Stable identity derived from the three keys.
    var id: String { "\(categoryID)|\(fromUnitID)|\(toUnitID)" }
}
