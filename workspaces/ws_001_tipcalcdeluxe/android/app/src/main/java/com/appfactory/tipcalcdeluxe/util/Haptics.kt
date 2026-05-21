package com.appfactory.tipcalcdeluxe.util

import androidx.compose.ui.hapticfeedback.HapticFeedback
import androidx.compose.ui.hapticfeedback.HapticFeedbackType

/**
 * Small helpers around Compose haptic feedback
 * (spec feature: "Haptic feedback on interactions").
 */
fun HapticFeedback.tap() {
    performHapticFeedback(HapticFeedbackType.TextHandleMove)
}

fun HapticFeedback.confirm() {
    performHapticFeedback(HapticFeedbackType.LongPress)
}
