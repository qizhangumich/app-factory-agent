package com.appfactory.qrbarcodescanner.ui

import android.content.Context
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager

/**
 * Lightweight haptic feedback helper. Used to confirm a successful scan
 * and minor UI taps. Degrades gracefully on devices without a vibrator.
 */
object Haptics {

    /** A short, distinct double-tick confirming a successful scan. */
    fun success(context: Context) {
        vibrator(context)?.let { v ->
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                v.vibrate(
                    VibrationEffect.createWaveform(
                        longArrayOf(0, 35, 60, 35), -1,
                    )
                )
            } else {
                @Suppress("DEPRECATION")
                v.vibrate(longArrayOf(0, 35, 60, 35), -1)
            }
        }
    }

    /** A single light tick for minor UI confirmations. */
    fun tick(context: Context) {
        vibrator(context)?.let { v ->
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                v.vibrate(VibrationEffect.createOneShot(20, 80))
            } else {
                @Suppress("DEPRECATION")
                v.vibrate(20)
            }
        }
    }

    private fun vibrator(context: Context): Vibrator? {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val manager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE)
                as? VibratorManager
            manager?.defaultVibrator
        } else {
            @Suppress("DEPRECATION")
            context.getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
        }?.takeIf { it.hasVibrator() }
    }
}
