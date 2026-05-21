package com.appfactory.tipcalcdeluxe.model

import java.text.NumberFormat
import java.util.Locale

/**
 * Locale-aware currency formatting. The currency symbol is detected from the
 * device locale (spec feature: "Currency symbol auto-detection from locale").
 */
object CurrencyFormatter {

    private val format: NumberFormat by lazy {
        NumberFormat.getCurrencyInstance(Locale.getDefault()).apply {
            maximumFractionDigits = 2
            minimumFractionDigits = 2
        }
    }

    /** The currency symbol for the current locale (e.g. "$", "£", "AED"). */
    val symbol: String
        get() = runCatching { format.currency?.symbol }.getOrNull() ?: "$"

    /** Format a monetary value using the current locale's currency style. */
    fun string(value: Double): String {
        val safe = if (value.isFinite()) value else 0.0
        return runCatching { format.format(safe) }.getOrDefault("$symbol%.2f".format(safe))
    }

    /** Parse a free-form numeric string from a text field into a Double. */
    fun parse(text: String): Double {
        if (text.isBlank()) return 0.0
        var cleaned = text.trim()
        // Strip the currency symbol and any grouping separators.
        cleaned = cleaned.replace(symbol, "")
        cleaned = cleaned.replace(",", "")
        cleaned = cleaned.replace(" ", "")
        return cleaned.toDoubleOrNull() ?: 0.0
    }
}
