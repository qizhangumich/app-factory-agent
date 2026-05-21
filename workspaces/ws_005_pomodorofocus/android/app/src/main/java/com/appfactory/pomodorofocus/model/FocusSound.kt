package com.appfactory.pomodorofocus.model

/** Optional looping focus sound played while a phase runs. */
enum class FocusSound(val storageValue: String) {
    SILENT("silent"),
    TICK("tick"),
    WHITE_NOISE("whiteNoise"),
    RAIN("rain");

    companion object {
        fun fromStorage(value: String): FocusSound =
            entries.firstOrNull { it.storageValue == value } ?: SILENT
    }
}
