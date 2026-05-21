package com.appfactory.tipcalcdeluxe.model

import android.content.Context
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.snapshots.SnapshotStateList
import org.json.JSONArray

/**
 * Persists the most recent 20 calculations to SharedPreferences
 * (spec.data_storage). Backed by a Compose snapshot list so the UI
 * recomposes automatically when history changes.
 */
class HistoryStore(context: Context) {

    private val prefs = context.applicationContext
        .getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    /** Observable list of calculations, newest first. */
    val entries: SnapshotStateList<TipCalculation> = mutableStateListOf()

    init {
        load()
    }

    /** Insert a new calculation at the front, trimming to [MAX_ENTRIES]. */
    fun add(calculation: TipCalculation) {
        entries.add(0, calculation)
        while (entries.size > MAX_ENTRIES) {
            entries.removeAt(entries.lastIndex)
        }
        save()
    }

    /** Remove a single entry by identity. */
    fun delete(calculation: TipCalculation) {
        entries.removeAll { it.id == calculation.id }
        save()
    }

    /** Remove all history. */
    fun clear() {
        entries.clear()
        save()
    }

    private fun load() {
        val raw = prefs.getString(KEY_HISTORY, null) ?: return
        runCatching {
            val array = JSONArray(raw)
            val loaded = ArrayList<TipCalculation>(array.length())
            for (i in 0 until array.length()) {
                loaded.add(TipCalculation.fromJson(array.getJSONObject(i)))
            }
            entries.clear()
            entries.addAll(loaded)
        }
    }

    private fun save() {
        val array = JSONArray()
        entries.forEach { array.put(it.toJson()) }
        prefs.edit().putString(KEY_HISTORY, array.toString()).apply()
    }

    companion object {
        const val MAX_ENTRIES = 20
        private const val PREFS_NAME = "tipcalc_prefs"
        private const val KEY_HISTORY = "history_v1"
    }
}
