package com.appfactory.unitconverterpro.model

import java.text.DecimalFormat
import kotlin.math.abs

/** Pure, stateless conversion math. All factors come from [UnitData]. */
object ConversionEngine {

    /**
     * Converts [value] from one unit to another within the same [category].
     * Returns null if either unit is not in the category.
     */
    fun convert(value: Double, from: ConvUnit, to: ConvUnit, category: UnitCategory): Double? {
        if (category.units.none { it.id == from.id }) return null
        if (category.units.none { it.id == to.id }) return null

        if (category.isTemperature) {
            return convertTemperature(value, from.id, to.id)
        }
        // Linear conversion: value -> base -> target.
        val base = value * from.factor
        return base / to.factor
    }

    /** Temperature conversion via Celsius as the pivot. */
    private fun convertTemperature(value: Double, fromId: String, toId: String): Double {
        val celsius = when (fromId) {
            "temperature.celsius" -> value
            "temperature.fahrenheit" -> (value - 32.0) * 5.0 / 9.0
            "temperature.kelvin" -> value - 273.15
            else -> value
        }
        return when (toId) {
            "temperature.celsius" -> celsius
            "temperature.fahrenheit" -> celsius * 9.0 / 5.0 + 32.0
            "temperature.kelvin" -> celsius + 273.15
            else -> celsius
        }
    }

    /**
     * Formats a numeric result for display. Uses scientific notation for very
     * large or very small magnitudes, otherwise a trimmed grouped decimal.
     */
    fun format(value: Double): String {
        if (value.isNaN()) return "—"
        if (value.isInfinite()) return if (value > 0) "∞" else "-∞"
        if (value == 0.0) return "0"

        val magnitude = abs(value)
        return if (magnitude >= 1e12 || magnitude < 1e-6) {
            DecimalFormat("0.######E0").format(value)
        } else {
            DecimalFormat("#,##0.########").format(value)
        }
    }

    /**
     * Parses user text into a Double, tolerating grouping separators and a
     * comma used as a decimal separator.
     */
    fun parse(text: String): Double? {
        val trimmed = text.trim()
        if (trimmed.isEmpty()) return null
        val normalized = trimmed
            .replace(" ", "")
            .replace(",", "")
        normalized.toDoubleOrNull()?.let { return it }
        // Retry treating the last comma as a decimal point.
        return trimmed.replace(" ", "").replace(",", ".").toDoubleOrNull()
    }

    /** Plain (no grouping) string of a value, suitable for re-seeding an input field. */
    fun plainString(value: Double): String {
        if (!value.isFinite()) return "0"
        val s = DecimalFormat("0.########").format(value)
        return s
    }
}
