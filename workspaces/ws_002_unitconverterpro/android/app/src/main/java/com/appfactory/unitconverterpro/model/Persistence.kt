package com.appfactory.unitconverterpro.model

/** A completed conversion recorded in history. */
data class HistoryEntry(
    val id: String,
    val categoryId: String,
    val fromUnitId: String,
    val toUnitId: String,
    val inputValue: Double,
    val resultValue: Double,
    val timestamp: Long
)

/** A starred conversion pair for quick access. */
data class FavoritePair(
    val categoryId: String,
    val fromUnitId: String,
    val toUnitId: String
) {
    /** Stable identity derived from the three keys. */
    val id: String get() = "$categoryId|$fromUnitId|$toUnitId"
}
