package com.appfactory.pomodorofocus.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.SkipNext
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.background
import androidx.compose.runtime.collectAsState
import com.appfactory.pomodorofocus.R
import com.appfactory.pomodorofocus.RunState
import com.appfactory.pomodorofocus.TimerViewModel
import com.appfactory.pomodorofocus.model.PomodoroPhase

/** Main screen: circular timer, session dots and transport controls. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TimerScreen(viewModel: TimerViewModel, modifier: Modifier = Modifier) {
    val state by viewModel.uiState.collectAsState()
    var showSettings by remember { mutableStateOf(false) }

    val phaseColor = state.phase.color
    val animatedProgress by animateFloatAsState(
        targetValue = state.progress,
        label = "ringProgress"
    )

    Column(
        modifier = modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        TopAppBar(
            title = { Text(stringResource(R.string.app_name)) },
            actions = {
                IconButton(onClick = { showSettings = true }) {
                    Icon(
                        Icons.Default.Settings,
                        contentDescription = stringResource(R.string.cd_open_settings)
                    )
                }
            }
        )

        Spacer(Modifier.height(24.dp))

        TimerRing(
            progress = animatedProgress,
            timeText = state.timeText,
            phaseLabel = phaseLabel(state.phase),
            phaseColor = phaseColor
        )

        Spacer(Modifier.height(32.dp))

        SessionDots(
            completed = state.completedInCycle.coerceAtMost(state.cycleLength),
            total = state.cycleLength.coerceAtLeast(1),
            color = phaseColor
        )

        Spacer(Modifier.height(40.dp))

        Controls(state.runState, phaseColor, viewModel)
    }

    if (showSettings) {
        SettingsSheet(viewModel) { showSettings = false }
    }
}

@Composable
private fun phaseLabel(phase: PomodoroPhase): String = stringResource(
    when (phase) {
        PomodoroPhase.FOCUS -> R.string.phase_focus
        PomodoroPhase.SHORT_BREAK -> R.string.phase_short
        PomodoroPhase.LONG_BREAK -> R.string.phase_long
    }
)

/** 250dp circular progress ring with the MM:SS label in the center. */
@Composable
private fun TimerRing(
    progress: Float,
    timeText: String,
    phaseLabel: String,
    phaseColor: Color
) {
    val trackColor = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.10f)
    Box(
        modifier = Modifier
            .size(250.dp)
            .semantics { contentDescription = "$phaseLabel $timeText" },
        contentAlignment = Alignment.Center
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val stroke = 18.dp.toPx()
            val arcSize = Size(size.width - stroke, size.height - stroke)
            val topLeft = androidx.compose.ui.geometry.Offset(stroke / 2, stroke / 2)
            // Track.
            drawArc(
                color = trackColor,
                startAngle = 0f,
                sweepAngle = 360f,
                useCenter = false,
                topLeft = topLeft,
                size = arcSize,
                style = Stroke(width = stroke, cap = StrokeCap.Round)
            )
            // Progress.
            drawArc(
                color = phaseColor,
                startAngle = -90f,
                sweepAngle = 360f * progress.coerceIn(0f, 1f),
                useCenter = false,
                topLeft = topLeft,
                size = arcSize,
                style = Stroke(width = stroke, cap = StrokeCap.Round)
            )
        }
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = phaseLabel.uppercase(),
                color = phaseColor,
                fontWeight = FontWeight.Bold,
                fontSize = 14.sp,
                letterSpacing = 2.sp
            )
            Text(
                text = timeText,
                fontSize = 60.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground
            )
        }
    }
}

/** Session progress dots: filled = completed focus session. */
@Composable
private fun SessionDots(completed: Int, total: Int, color: Color) {
    Row(
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        modifier = Modifier.semantics {
            contentDescription = "Session progress $completed of $total"
        }
    ) {
        repeat(total) { index ->
            Box(
                modifier = Modifier
                    .size(12.dp)
                    .clip(CircleShape)
                    .background(
                        if (index < completed) color
                        else color.copy(alpha = 0.18f)
                    )
            )
        }
    }
}

/** Start/Pause primary button plus Reset / Skip secondaries. */
@Composable
private fun Controls(
    runState: RunState,
    phaseColor: Color,
    viewModel: TimerViewModel
) {
    val primaryLabel = stringResource(
        when (runState) {
            RunState.RUNNING -> R.string.control_pause
            RunState.PAUSED -> R.string.control_resume
            RunState.IDLE -> R.string.control_start
        }
    )

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Button(
            onClick = { viewModel.onStartPause() },
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            colors = ButtonDefaults.buttonColors(containerColor = phaseColor)
        ) {
            Text(primaryLabel, fontSize = 18.sp, fontWeight = FontWeight.Bold)
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            OutlinedButton(
                onClick = { viewModel.onReset() },
                modifier = Modifier
                    .weight(1f)
                    .height(48.dp)
            ) {
                Icon(Icons.Default.Refresh, contentDescription = null)
                Spacer(Modifier.size(6.dp))
                Text(stringResource(R.string.control_reset))
            }
            OutlinedButton(
                onClick = { viewModel.onSkip() },
                modifier = Modifier
                    .weight(1f)
                    .height(48.dp)
            ) {
                Icon(Icons.Default.SkipNext, contentDescription = null)
                Spacer(Modifier.size(6.dp))
                Text(stringResource(R.string.control_skip))
            }
        }
    }
}
