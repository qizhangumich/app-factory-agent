package com.appfactory.unitconverterpro.data

import android.content.Context
import android.content.SharedPreferences
import com.appfactory.unitconverterpro.model.FavoritePair
import com.appfactory.unitconverterpro.model.HistoryEntry
import org.json.JSONArray
import org.json.JSONObject

/**
 * Persistence for favorites and history backed by [SharedPreferences].
 *
 * Data is serialized to compact JSON strings. No third-party serialization
 * library is used, keeping the dependency surface minimal. History is capped
 * at the most recent [HISTORY_LIMIT] entries.
 */
class PrefsRepository(context: Context) {

    companion object {
        const val HISTORY_LIMIT = 100
        private const val PREFS_NAME = "ucp_prefs"
        private const val KEY_FAVORITES = "favorites_v1"
        private const val KEY_HISTORY = "history_v1"
    }

    private val prefs: SharedPreferences =
        context.applicationContext.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    // MARK: - Favorites

    fun loadFavorites(): List<FavoritePair> {
        val raw = prefs.getString(KEY_FAVORITES, null) ?: return emptyList()
        return runCatching {
            val arr = JSONArray(raw)
            buildList {
                for (i in 0 until arr.length()) {
                    val o = arr.getJSONObject(i)
                    add(
                        FavoritePair(
                            categoryId = o.getString("c"),
                            fromUnitId = o.getString("f"),
                            toUnitId = o.getString("t")
                        )
                    )
                }
            }
        }.getOrDefault(emptyList())
    }

    fun saveFavorites(favorites: List<FavoritePair>) {
        val arr = JSONArray()
        favorites.forEach { fav ->
            arr.put(
                JSONObject().apply {
                    put("c", fav.categoryId)
                    put("f", fav.fromUnitId)
                    put("t", fav.toUnitId)
                }
            )
        }
        prefs.edit().putString(KEY_FAVORITES, arr.toString()).apply()
    }

    // MARK: - History

    fun loadHistory(): List<HistoryEntry> {
        val raw = prefs.getString(KEY_HISTORY, null) ?: return emptyList()
        return runCatching {
            val arr = JSONArray(raw)
            buildList {
                for (i in 0 until arr.length()) {
                    val o = arr.getJSONObject(i)
                    add(
                        HistoryEntry(
                            id = o.getString("id"),
                            categoryId = o.getString("c"),
                            fromUnitId = o.getString("f"),
                            toUnitId = o.getString("t"),
                            inputValue = o.getDouble("iv"),
                            resultValue = o.getDouble("rv"),
                            timestamp = o.getLong("ts")
                        )
                    )
                }
            }
        }.getOrDefault(emptyList())
    }

    fun saveHistory(history: List<HistoryEntry>) {
        val arr = JSONArray()
        history.take(HISTORY_LIMIT).forEach { e ->
            arr.put(
                JSONObject().apply {
                    put("id", e.id)
                    put("c", e.categoryId)
                    put("f", e.fromUnitId)
                    put("t", e.toUnitId)
                    put("iv", e.inputValue)
                    put("rv", e.resultValue)
                    put("ts", e.timestamp)
                }
            )
        }
        prefs.edit().putString(KEY_HISTORY, arr.toString()).apply()
    }
}
