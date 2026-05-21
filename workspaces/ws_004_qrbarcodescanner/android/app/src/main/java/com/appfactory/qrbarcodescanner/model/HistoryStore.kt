package com.appfactory.qrbarcodescanner.model

import android.content.Context
import android.content.SharedPreferences
import org.json.JSONArray
import org.json.JSONException

/**
 * Persists the scan history (most recent [MAX_ENTRIES] entries) to
 * [SharedPreferences] as a JSON array. All data stays on-device.
 */
class HistoryStore(context: Context) {

    private val prefs: SharedPreferences =
        context.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    /** Loads all stored scans, newest first. */
    fun load(): List<ScanResult> {
        val raw = prefs.getString(KEY, null) ?: return emptyList()
        return try {
            val array = JSONArray(raw)
            buildList {
                for (i in 0 until array.length()) {
                    add(ScanResult.fromJson(array.getJSONObject(i)))
                }
            }
        } catch (e: JSONException) {
            // Corrupt data: start clean rather than crash.
            emptyList()
        }
    }

    /** Persists [scans], trimming to [MAX_ENTRIES]. */
    fun save(scans: List<ScanResult>) {
        val trimmed = scans.take(MAX_ENTRIES)
        val array = JSONArray()
        trimmed.forEach { array.put(it.toJson()) }
        prefs.edit().putString(KEY, array.toString()).apply()
    }

    companion object {
        const val MAX_ENTRIES = 200
        private const val PREFS = "qrbarcodescanner_history"
        private const val KEY = "history_v1"
    }
}
