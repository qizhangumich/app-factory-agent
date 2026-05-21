package com.appfactory.qrbarcodescanner

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import com.appfactory.qrbarcodescanner.model.HistoryStore
import com.appfactory.qrbarcodescanner.model.ScanResult
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Holds all UI state for the app: the scan history, the currently
 * presented result, the torch state, and transient flags.
 *
 * History is loaded from [HistoryStore] on construction and saved back
 * after every mutation, so the last 200 scans survive process death.
 */
class ScannerViewModel(app: Application) : AndroidViewModel(app) {

    private val store = HistoryStore(app)

    private val _history = MutableStateFlow(store.load())
    /** All saved scans, newest first. */
    val history: StateFlow<List<ScanResult>> = _history.asStateFlow()

    private val _currentResult = MutableStateFlow<ScanResult?>(null)
    /** The scan currently shown in the result sheet, or null. */
    val currentResult: StateFlow<ScanResult?> = _currentResult.asStateFlow()

    private val _torchOn = MutableStateFlow(false)
    /** Whether the flashlight is on. */
    val torchOn: StateFlow<Boolean> = _torchOn.asStateFlow()

    private val _importError = MutableStateFlow<String?>(null)
    /** Set when a photo import found no code; cleared when acknowledged. */
    val importError: StateFlow<String?> = _importError.asStateFlow()

    /**
     * Records a freshly scanned code: adds it to history (de-duplicating an
     * immediate repeat of the same value) and presents it as the result.
     */
    fun onScanned(result: ScanResult) {
        val list = _history.value
        val updated = if (list.firstOrNull()?.value == result.value) {
            // Same as most recent: refresh in place rather than duplicate.
            listOf(result) + list.drop(1)
        } else {
            (listOf(result) + list).take(HistoryStore.MAX_ENTRIES)
        }
        _history.value = updated
        store.save(updated)
        _currentResult.value = result
    }

    /** Dismisses the result sheet and resumes live scanning. */
    fun dismissResult() {
        _currentResult.value = null
    }

    /** Removes a single scan from history. */
    fun delete(result: ScanResult) {
        val updated = _history.value.filterNot { it.id == result.id }
        _history.value = updated
        store.save(updated)
    }

    /** Clears the entire scan history. */
    fun clearHistory() {
        _history.value = emptyList()
        store.save(emptyList())
    }

    /** Toggles the requested torch state. */
    fun toggleTorch() {
        _torchOn.value = !_torchOn.value
    }

    /** Forces the torch off (e.g. when leaving the scanner screen). */
    fun torchOff() {
        _torchOn.value = false
    }

    /** Reports that a photo import found no readable code. */
    fun reportImportFailure(message: String) {
        _importError.value = message
    }

    /** Clears the import-error flag. */
    fun clearImportError() {
        _importError.value = null
    }

    /** Returns history entries matching a case-insensitive query. */
    fun filtered(query: String): List<ScanResult> {
        val q = query.trim()
        if (q.isEmpty()) return _history.value
        return _history.value.filter {
            it.value.contains(q, ignoreCase = true) ||
                it.symbology.contains(q, ignoreCase = true) ||
                it.contentType.displayName.contains(q, ignoreCase = true)
        }
    }

    /** Looks up a scan by id (used to restore detail screen after rotation). */
    fun find(id: String): ScanResult? = _history.value.firstOrNull { it.id == id }
}
