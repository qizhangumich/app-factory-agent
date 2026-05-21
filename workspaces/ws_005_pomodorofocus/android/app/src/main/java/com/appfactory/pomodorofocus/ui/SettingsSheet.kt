package com.appfactory.pomodorofocus.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Remove
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Divider
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledTonalIconButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.appfactory.pomodorofocus.R
import com.appfactory.pomodorofocus.TimerViewModel
import com.appfactory.pomodorofocus.model.FocusSound
import com.appfactory.pomodorofocus.model.TimerSettings

/** Bottom-sheet settings panel — configures every timer parameter. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsSheet(viewModel: TimerViewModel, onDismiss: () -> Unit) {
    val settings by viewModel.settings.collectAsState()
    var showResetDialog by remember { mutableStateOf(false) }

    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp)
                .padding(bottom = 32.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(
                stringResource(R.string.settings_title),
                style = MaterialTheme.typography.titleLarge,
                modifier = Modifier.padding(vertical = 8.dp)
            )

            SectionHeader(stringResource(R.string.settings_section_durations))
            StepperRow(
                label = stringResource(R.string.settings_focus),
                value = settings.focusMinutes,
                range = TimerSettings.FOCUS_RANGE,
                unit = stringResource(R.string.unit_min)
            ) { v -> viewModel.updateSettings { it.copy(focusMinutes = v) } }
            StepperRow(
                label = stringResource(R.string.settings_short_break),
                value = settings.shortBreakMinutes,
                range = TimerSettings.SHORT_BREAK_RANGE,
                unit = stringResource(R.string.unit_min)
            ) { v -> viewModel.updateSettings { it.copy(shortBreakMinutes = v) } }
            StepperRow(
                label = stringResource(R.string.settings_long_break),
                value = settings.longBreakMinutes,
                range = TimerSettings.LONG_BREAK_RANGE,
                unit = stringResource(R.string.unit_min)
            ) { v -> viewModel.updateSettings { it.copy(longBreakMinutes = v) } }

            SectionHeader(stringResource(R.string.settings_section_cycle))
            StepperRow(
                label = stringResource(R.string.settings_sessions_until_long),
                value = settings.sessionsUntilLongBreak,
                range = TimerSettings.CYCLE_RANGE,
                unit = ""
            ) { v -> viewModel.updateSettings { it.copy(sessionsUntilLongBreak = v) } }

            SectionHeader(stringResource(R.string.settings_section_behavior))
            SwitchRow(
                label = stringResource(R.string.settings_auto_start),
                checked = settings.autoStartNext
            ) { v -> viewModel.updateSettings { it.copy(autoStartNext = v) } }

            SectionHeader(stringResource(R.string.settings_section_sound))
            SoundPickerRow(settings.focusSound) { sound ->
                viewModel.updateSettings { it.copy(focusSound = sound) }
            }

            SectionHeader(stringResource(R.string.settings_section_appearance))
            SwitchRow(
                label = stringResource(R.string.settings_notifications),
                checked = settings.notificationsEnabled
            ) { v -> viewModel.updateSettings { it.copy(notificationsEnabled = v) } }
            SwitchRow(
                label = stringResource(R.string.settings_true_black),
                checked = settings.trueBlackMode
            ) { v -> viewModel.updateSettings { it.copy(trueBlackMode = v) } }

            SectionHeader(stringResource(R.string.settings_section_data))
            TextButton(onClick = { showResetDialog = true }) {
                Text(
                    stringResource(R.string.settings_reset_stats),
                    color = MaterialTheme.colorScheme.error
                )
            }
        }
    }

    if (showResetDialog) {
        AlertDialog(
            onDismissRequest = { showResetDialog = false },
            title = { Text(stringResource(R.string.settings_reset_title)) },
            text = { Text(stringResource(R.string.settings_reset_message)) },
            confirmButton = {
                TextButton(onClick = {
                    viewModel.onResetStats()
                    showResetDialog = false
                }) {
                    Text(
                        stringResource(R.string.settings_reset_confirm),
                        color = MaterialTheme.colorScheme.error
                    )
                }
            },
            dismissButton = {
                TextButton(onClick = { showResetDialog = false }) {
                    Text(stringResource(R.string.common_cancel))
                }
            }
        )
    }
}

@Composable
private fun SectionHeader(text: String) {
    Spacer(Modifier.height(8.dp))
    Text(
        text,
        style = MaterialTheme.typography.labelLarge,
        color = MaterialTheme.colorScheme.primary,
        fontWeight = FontWeight.Bold
    )
    Divider(Modifier.padding(vertical = 4.dp))
}

/** A label with -/+ buttons that clamps to [range]. */
@Composable
private fun StepperRow(
    label: String,
    value: Int,
    range: IntRange,
    unit: String,
    onChange: (Int) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(label, modifier = Modifier.weight(1f))
        FilledTonalIconButton(
            onClick = { if (value > range.first) onChange(value - 1) }
        ) {
            Icon(Icons.Default.Remove, contentDescription = "Decrease $label")
        }
        Text(
            text = if (unit.isEmpty()) "$value" else "$value $unit",
            modifier = Modifier
                .padding(horizontal = 12.dp)
                .width(64.dp),
            textAlign = androidx.compose.ui.text.style.TextAlign.Center,
            fontWeight = FontWeight.SemiBold
        )
        FilledTonalIconButton(
            onClick = { if (value < range.last) onChange(value + 1) }
        ) {
            Icon(Icons.Default.Add, contentDescription = "Increase $label")
        }
    }
}

@Composable
private fun SwitchRow(label: String, checked: Boolean, onChange: (Boolean) -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(label, modifier = Modifier.weight(1f))
        Switch(checked = checked, onCheckedChange = onChange)
    }
}

@Composable
private fun SoundPickerRow(current: FocusSound, onPick: (FocusSound) -> Unit) {
    var expanded by remember { mutableStateOf(false) }
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(stringResource(R.string.settings_focus_sound), modifier = Modifier.weight(1f))
        TextButton(onClick = { expanded = true }) {
            Text(soundLabel(current))
        }
        DropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
            FocusSound.entries.forEach { sound ->
                DropdownMenuItem(
                    text = { Text(soundLabel(sound)) },
                    onClick = {
                        onPick(sound)
                        expanded = false
                    }
                )
            }
        }
    }
}

@Composable
private fun soundLabel(sound: FocusSound): String = stringResource(
    when (sound) {
        FocusSound.SILENT -> R.string.sound_silent
        FocusSound.TICK -> R.string.sound_tick
        FocusSound.WHITE_NOISE -> R.string.sound_white_noise
        FocusSound.RAIN -> R.string.sound_rain
    }
)
