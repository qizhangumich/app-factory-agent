package com.appfactory.tipcalcdeluxe.ui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Undo
import androidx.compose.material.icons.filled.HistoryToggleOff
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.appfactory.tipcalcdeluxe.model.CurrencyFormatter
import com.appfactory.tipcalcdeluxe.model.HistoryStore
import com.appfactory.tipcalcdeluxe.model.TipCalculation
import com.appfactory.tipcalcdeluxe.util.tap
import java.text.DateFormat
import java.util.Date
import kotlin.math.roundToInt

/**
 * Bottom-sheet content showing the last 20 saved calculations
 * (spec component "History button").
 */
@Composable
fun HistorySheetContent(
    history: HistoryStore,
    onSelect: (TipCalculation) -> Unit
) {
    val haptics = LocalHapticFeedback.current

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp)
            .padding(bottom = 24.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                "History",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            if (history.entries.isNotEmpty()) {
                TextButton(onClick = {
                    haptics.tap()
                    history.clear()
                }) {
                    Text("Clear All")
                }
            }
        }
        Spacer(Modifier.size(8.dp))

        if (history.entries.isEmpty()) {
            EmptyHistory()
        } else {
            LazyColumn(
                modifier = Modifier.heightIn(max = 420.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                items(history.entries, key = { it.id }) { entry ->
                    HistoryRow(
                        entry = entry,
                        onClick = { onSelect(entry) },
                        onDelete = {
                            haptics.tap()
                            history.delete(entry)
                        }
                    )
                    HorizontalDivider()
                }
            }
        }
    }
}

@Composable
private fun EmptyHistory() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 40.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Icon(
            Icons.Filled.HistoryToggleOff,
            contentDescription = null,
            modifier = Modifier.size(48.dp),
            tint = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            "No Calculations Yet",
            style = MaterialTheme.typography.titleMedium
        )
        Text(
            "Saved calculations appear here. Your last 20 are kept.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun HistoryRow(
    entry: TipCalculation,
    onClick: () -> Unit,
    onDelete: () -> Unit
) {
    val dateText = remember(entry.timestamp) {
        DateFormat.getDateTimeInstance(DateFormat.MEDIUM, DateFormat.SHORT)
            .format(Date(entry.timestamp))
    }
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() }
            .padding(vertical = 10.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(
                CurrencyFormatter.string(entry.totalPerPerson),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.tertiary
            )
            Text(
                "${CurrencyFormatter.string(entry.billAmount)} bill - " +
                    "${entry.tipPercent.roundToInt()}% tip - " +
                    "${entry.people} ${if (entry.people == 1) "person" else "people"}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                dateText,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
        IconButton(onClick = onClick) {
            Icon(
                Icons.AutoMirrored.Filled.Undo,
                contentDescription = "Restore this calculation",
                tint = MaterialTheme.colorScheme.primary
            )
        }
        TextButton(onClick = onDelete) {
            Text("Delete")
        }
    }
}
