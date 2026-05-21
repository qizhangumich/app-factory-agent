package com.appfactory.tipcalcdeluxe.model

import org.json.JSONObject
import java.util.UUID

/**
 * An immutable result of a tip calculation. Persisted to SharedPreferences
 * as JSON (the app keeps the most recent 20 — see [HistoryStore]).
 */
data class TipCalculation(
    val id: String = UUID.randomUUID().toString(),
    val timestamp: Long = System.currentTimeMillis(),
    val billAmount: Double,
    val tipPercent: Double,
    val taxEnabled: Boolean,
    val taxPercent: Double,
    val people: Int,
    val isUnequalSplit: Boolean,
    val rounding: Rounding
) {
    val tipAmount: Double get() = billAmount * tipPercent / 100.0

    val taxAmount: Double get() = if (taxEnabled) billAmount * taxPercent / 100.0 else 0.0

    /** Grand total before the rounding mode is applied. */
    val rawTotal: Double get() = billAmount + tipAmount + taxAmount

    /** Grand total after the rounding mode is applied. */
    val grandTotal: Double get() = rounding.apply(rawTotal)

    val totalPerPerson: Double get() = if (people > 0) grandTotal / people else 0.0

    val tipPerPerson: Double get() = if (people > 0) tipAmount / people else 0.0

    val taxPerPerson: Double get() = if (people > 0) taxAmount / people else 0.0

    /** Serialize to a JSON object for persistence. */
    fun toJson(): JSONObject = JSONObject().apply {
        put("id", id)
        put("timestamp", timestamp)
        put("billAmount", billAmount)
        put("tipPercent", tipPercent)
        put("taxEnabled", taxEnabled)
        put("taxPercent", taxPercent)
        put("people", people)
        put("isUnequalSplit", isUnequalSplit)
        put("rounding", rounding.name)
    }

    companion object {
        /** Recreate a calculation from a persisted JSON object. */
        fun fromJson(json: JSONObject): TipCalculation = TipCalculation(
            id = json.optString("id", UUID.randomUUID().toString()),
            timestamp = json.optLong("timestamp", System.currentTimeMillis()),
            billAmount = json.optDouble("billAmount", 0.0),
            tipPercent = json.optDouble("tipPercent", 18.0),
            taxEnabled = json.optBoolean("taxEnabled", false),
            taxPercent = json.optDouble("taxPercent", 0.0),
            people = json.optInt("people", 1),
            isUnequalSplit = json.optBoolean("isUnequalSplit", false),
            rounding = runCatching {
                Rounding.valueOf(json.optString("rounding", Rounding.NONE.name))
            }.getOrDefault(Rounding.NONE)
        )
    }
}
