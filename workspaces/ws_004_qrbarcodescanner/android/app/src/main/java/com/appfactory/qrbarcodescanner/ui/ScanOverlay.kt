package com.appfactory.qrbarcodescanner.ui

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.BlendMode
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.unit.dp
import kotlin.math.min

/**
 * Translucent scan-target reticle drawn over the camera preview: a dimmed
 * mask with a clear rounded window and bright corner brackets. The
 * brackets flash green ([flashSuccess]) on a successful scan.
 */
@Composable
fun ScanOverlay(
    flashSuccess: Boolean,
    modifier: Modifier = Modifier,
) {
    val cornerColor by animateColorAsState(
        targetValue = if (flashSuccess) ScanSuccess else Color.White,
        animationSpec = tween(200),
        label = "cornerColor",
    )

    Canvas(modifier = modifier.fillMaxSize()) {
        val side = min(size.width, size.height) * 0.68f
        val left = (size.width - side) / 2f
        val top = (size.height - side) / 2f
        val radius = 24.dp.toPx()
        val cornerLen = side * 0.12f
        val strokeWidth = 5.dp.toPx()
        val right = left + side
        val bottom = top + side

        // Dimmed mask everywhere except the scan window.
        drawRect(color = Color.Black.copy(alpha = 0.45f))
        drawRoundRect(
            color = Color.Transparent,
            topLeft = Offset(left, top),
            size = Size(side, side),
            cornerRadius = CornerRadius(radius, radius),
            blendMode = BlendMode.Clear,
        )

        // Subtle full border.
        drawRoundRect(
            color = cornerColor.copy(alpha = 0.5f),
            topLeft = Offset(left, top),
            size = Size(side, side),
            cornerRadius = CornerRadius(radius, radius),
            style = Stroke(width = 2.dp.toPx()),
        )

        // Bright L-shaped corner brackets.
        val path = Path().apply {
            // top-left
            moveTo(left, top + cornerLen)
            lineTo(left, top)
            lineTo(left + cornerLen, top)
            // top-right
            moveTo(right - cornerLen, top)
            lineTo(right, top)
            lineTo(right, top + cornerLen)
            // bottom-left
            moveTo(left, bottom - cornerLen)
            lineTo(left, bottom)
            lineTo(left + cornerLen, bottom)
            // bottom-right
            moveTo(right - cornerLen, bottom)
            lineTo(right, bottom)
            lineTo(right, bottom - cornerLen)
        }
        drawPath(
            path = path,
            color = cornerColor,
            style = Stroke(width = strokeWidth, cap = StrokeCap.Round),
        )
    }
}
