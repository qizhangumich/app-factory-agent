package com.appfactory.tipcalcdeluxe.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Save
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.unit.dp
import com.appfactory.tipcalcdeluxe.model.CalculatorViewModel
import com.appfactory.tipcalcdeluxe.model.HistoryStore
import com.appfactory.tipcalcdeluxe.util.confirm
import kotlinx.coroutines.delay

/** Saves the current calculation to history with a brief confirmation. */
@Composable
fun SaveButton(viewModel: CalculatorViewModel, history: HistoryStore) {
    val haptics = LocalHapticFeedback.current
    var justSaved by remember { mutableStateOf(false) }

    LaunchedEffect(justSaved) {
        if (justSaved) {
            delay(1600)
            justSaved = false
        }
    }

    Button(
        onClick = {
            if (viewModel.saveToHistory(history)) {
                haptics.confirm()
                justSaved = true
            }
        },
        enabled = viewModel.hasBill,
        modifier = Modifier
            .fillMaxWidth()
            .height(52.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = if (justSaved) {
                MaterialTheme.colorScheme.tertiary
            } else {
                MaterialTheme.colorScheme.primary
            }
        )
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = if (justSaved) Icons.Filled.CheckCircle else Icons.Filled.Save,
                contentDescription = null
            )
            Spacer(Modifier.width(8.dp))
            Text(if (justSaved) "Saved to History" else "Save Calculation")
        }
    }
}
