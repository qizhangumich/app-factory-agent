package com.appfactory.unitconverterpro

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.appfactory.unitconverterpro.data.PrefsRepository
import com.appfactory.unitconverterpro.model.FavoritePair
import com.appfactory.unitconverterpro.model.HistoryEntry
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.util.UUID

/**
 * Single shared view model. Owns favorites and history, and exposes them as
 * [StateFlow] so all screens stay in sync. Persists every mutation.
 */
class ConverterViewModel(app: Application) : AndroidViewModel(app) {

    private val repo = PrefsRepository(app)

    private val _favorites = MutableStateFlow(repo.loadFavorites())
    val favorites: StateFlow<List<FavoritePair>> = _favorites.asStateFlow()

    private val _history = MutableStateFlow(repo.loadHistory())
    val history: StateFlow<List<HistoryEntry>> = _history.asStateFlow()

    // MARK: - Favorites

    fun isFavorite(categoryId: String, fromUnitId: String, toUnitId: String): Boolean =
        _favorites.value.any {
            it.categoryId == categoryId &&
                it.fromUnitId == fromUnitId &&
                it.toUnitId == toUnitId
        }

    fun toggleFavorite(categoryId: String, fromUnitId: String, toUnitId: String) {
        val pair = FavoritePair(categoryId, fromUnitId, toUnitId)
        val current = _favorites.value
        val updated = if (current.any { it.id == pair.id }) {
            current.filterNot { it.id == pair.id }
        } else {
            listOf(pair) + current
        }
        _favorites.value = updated
        persistFavorites(updated)
    }

    fun removeFavorite(pair: FavoritePair) {
        val updated = _favorites.value.filterNot { it.id == pair.id }
        _favorites.value = updated
        persistFavorites(updated)
    }

    // MARK: - History

    /** Records a conversion. Ignores non-finite values to keep history clean. */
    fun addHistory(
        categoryId: String,
        fromUnitId: String,
        toUnitId: String,
        inputValue: Double,
        resultValue: Double
    ) {
        if (!inputValue.isFinite() || !resultValue.isFinite()) return
        val entry = HistoryEntry(
            id = UUID.randomUUID().toString(),
            categoryId = categoryId,
            fromUnitId = fromUnitId,
            toUnitId = toUnitId,
            inputValue = inputValue,
            resultValue = resultValue,
            timestamp = System.currentTimeMillis()
        )
        val updated = (listOf(entry) + _history.value).take(PrefsRepository.HISTORY_LIMIT)
        _history.value = updated
        persistHistory(updated)
    }

    fun deleteHistory(entry: HistoryEntry) {
        val updated = _history.value.filterNot { it.id == entry.id }
        _history.value = updated
        persistHistory(updated)
    }

    fun clearHistory() {
        _history.value = emptyList()
        persistHistory(emptyList())
    }

    // MARK: - Persistence helpers

    private fun persistFavorites(list: List<FavoritePair>) {
        viewModelScope.launch { repo.saveFavorites(list) }
    }

    private fun persistHistory(list: List<HistoryEntry>) {
        viewModelScope.launch { repo.saveHistory(list) }
    }
}
