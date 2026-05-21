package com.appfactory.tipcalcdeluxe.model

import kotlin.math.ceil
import kotlin.math.floor

/** Rounding mode applied to the grand total of the bill. */
enum class Rounding(val label: String) {
    NONE("Exact"),
    DOWN("Round Down"),
    UP("Round Up");

    /** Apply this rounding mode to a grand total. */
    fun apply(total: Double): Double = when (this) {
        NONE -> total
        DOWN -> floor(total)
        UP -> ceil(total)
    }
}
