package com.appfactory.tipcalcdeluxe.model

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshots.SnapshotStateList
import androidx.lifecycle.ViewModel

/**
 * Holds all calculator input and derives the live result. Compose state
 * is used directly so the single screen recomposes as the user types.
 */
class CalculatorViewModel : ViewModel() {

    // ---- Limits ----
    val minPeople = 1
    val maxPeople = 20
    val minTip = 0f
    val maxTip = 50f

    // ---- User input ----
    var billText by mutableStateOf("")
    var tipPercent by mutableStateOf(18f)            // 0..50, default 18
    var taxEnabled by mutableStateOf(false)          // default off
    var taxText by mutableStateOf("8")
    var people by mutableStateOf(2)                  // 1..20, default 2
    var isUnequalSplit by mutableStateOf(false)
    var rounding by mutableStateOf(Rounding.NONE)

    /** Per-person weights for an unequal split; always [people] entries long. */
    val customWeights: SnapshotStateList<Float> = mutableStateListOf(1f, 1f)

    // ---- Derived input ----
    val billAmount: Double get() = CurrencyFormatter.parse(billText)

    val taxPercent: Double get() = CurrencyFormatter.parse(taxText).coerceAtLeast(0.0)

    val hasBill: Boolean get() = billAmount > 0.0

    /** A snapshot of the current calculation (not yet persisted). */
    val calculation: TipCalculation
        get() = TipCalculation(
            billAmount = billAmount,
            tipPercent = tipPercent.toDouble(),
            taxEnabled = taxEnabled,
            taxPercent = taxPercent,
            people = people,
            isUnequalSplit = isUnequalSplit,
            rounding = rounding
        )

    val tipAmount: Double get() = calculation.tipAmount
    val taxAmount: Double get() = calculation.taxAmount
    val grandTotal: Double get() = calculation.grandTotal
    val totalPerPerson: Double get() = calculation.totalPerPerson
    val tipPerPerson: Double get() = calculation.tipPerPerson
    val taxPerPerson: Double get() = calculation.taxPerPerson

    /** Sum of all custom weights, never zero. */
    private val weightTotal: Double
        get() {
            val sum = customWeights.sumOf { it.toDouble() }
            return if (sum > 0) sum else 1.0
        }

    /** Amount owed by the person at [index] for an unequal split. */
    fun unequalShare(index: Int): Double {
        if (index !in customWeights.indices) return 0.0
        return grandTotal * customWeights[index] / weightTotal
    }

    // ---- People management ----
    fun incrementPeople() {
        if (people < maxPeople) {
            people += 1
            syncWeights()
        }
    }

    fun decrementPeople() {
        if (people > minPeople) {
            people -= 1
            syncWeights()
        }
    }

    /** Keep [customWeights] exactly [people] entries long. */
    fun syncWeights() {
        while (customWeights.size < people) customWeights.add(1f)
        while (customWeights.size > people) customWeights.removeAt(customWeights.lastIndex)
    }

    fun setWeight(index: Int, value: Float) {
        syncWeights()
        if (index in customWeights.indices) {
            customWeights[index] = value.coerceAtLeast(0f)
        }
    }

    // ---- Actions ----

    /** Persist the current calculation. Returns true if it was saved. */
    fun saveToHistory(store: HistoryStore): Boolean {
        if (!hasBill) return false
        store.add(calculation)
        return true
    }

    /** Restore calculator inputs from a history entry. */
    fun restore(entry: TipCalculation) {
        billText = "%.2f".format(entry.billAmount)
        tipPercent = entry.tipPercent.toFloat().coerceIn(minTip, maxTip)
        taxEnabled = entry.taxEnabled
        taxText = if (entry.taxPercent % 1.0 == 0.0) {
            entry.taxPercent.toInt().toString()
        } else {
            entry.taxPercent.toString()
        }
        people = entry.people.coerceIn(minPeople, maxPeople)
        isUnequalSplit = entry.isUnequalSplit
        rounding = entry.rounding
        syncWeights()
    }

    /** Reset every input to its default state. */
    fun reset() {
        billText = ""
        tipPercent = 18f
        taxEnabled = false
        taxText = "8"
        people = 2
        isUnequalSplit = false
        rounding = Rounding.NONE
        customWeights.clear()
        customWeights.addAll(listOf(1f, 1f))
    }
}
