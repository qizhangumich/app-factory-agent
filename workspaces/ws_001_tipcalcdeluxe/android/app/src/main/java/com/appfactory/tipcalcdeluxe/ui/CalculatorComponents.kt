package com.appfactory.tipcalcdeluxe.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Remove
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.SegmentedButton
import androidx.compose.material3.SegmentedButtonDefaults
import androidx.compose.material3.SingleChoiceSegmentedButtonRow
import androidx.compose.material3.Slider
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.appfactory.tipcalcdeluxe.model.CalculatorViewModel
import com.appfactory.tipcalcdeluxe.model.CurrencyFormatter
import com.appfactory.tipcalcdeluxe.model.Rounding
import com.appfactory.tipcalcdeluxe.util.tap
import kotlin.math.roundToInt

/** Bill amount input — numeric keyboard (spec component). */
@Composable
fun BillAmountField(viewModel: CalculatorViewModel) {
    SectionCard {
        Text(
            text = "Bill Amount",
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(Modifier.size(8.dp))
        OutlinedTextField(
            value = viewModel.billText,
            onValueChange = { new ->
                // Allow only digits and a single decimal separator.
                if (new.isEmpty() || new.matches(Regex("^\\d*[.,]?\\d{0,2}$"))) {
                    viewModel.billText = new
                }
            },
            singleLine = true,
            prefix = { Text(CurrencyFormatter.symbol) },
            placeholder = { Text("0.00") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
            modifier = Modifier
                .fillMaxWidth()
                .semantics { contentDescription = "Bill amount" }
        )
    }
}

/** Tip percentage slider — 0-50%, default 18% (spec component). */
@Composable
fun TipSliderCard(viewModel: CalculatorViewModel) {
    val haptics = LocalHapticFeedback.current
    val presets = listOf(10, 15, 18, 20, 25)

    SectionCard {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("Tip", style = MaterialTheme.typography.labelLarge)
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "${viewModel.tipPercent.roundToInt()}%",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
                Spacer(Modifier.width(8.dp))
                Text(
                    CurrencyFormatter.string(viewModel.tipAmount),
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.tertiary
                )
            }
        }
        Slider(
            value = viewModel.tipPercent,
            onValueChange = {
                viewModel.tipPercent = it
                haptics.tap()
            },
            valueRange = viewModel.minTip..viewModel.maxTip,
            steps = 49,
            modifier = Modifier.semantics {
                contentDescription = "Tip percentage slider"
            }
        )
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            presets.forEach { preset ->
                FilterChip(
                    selected = viewModel.tipPercent.roundToInt() == preset,
                    onClick = {
                        haptics.tap()
                        viewModel.tipPercent = preset.toFloat()
                    },
                    label = { Text("$preset%") },
                    modifier = Modifier.semantics {
                        contentDescription = "Set tip to $preset percent"
                    }
                )
            }
        }
    }
}

/** Tax toggle + configurable rate — default off (spec component). */
@Composable
fun TaxControlCard(viewModel: CalculatorViewModel) {
    val haptics = LocalHapticFeedback.current
    SectionCard {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("Add Tax", style = MaterialTheme.typography.labelLarge)
            Row(verticalAlignment = Alignment.CenterVertically) {
                if (viewModel.taxEnabled) {
                    Text(
                        CurrencyFormatter.string(viewModel.taxAmount),
                        style = MaterialTheme.typography.titleSmall,
                        color = MaterialTheme.colorScheme.tertiary
                    )
                    Spacer(Modifier.width(12.dp))
                }
                Switch(
                    checked = viewModel.taxEnabled,
                    onCheckedChange = {
                        haptics.tap()
                        viewModel.taxEnabled = it
                    },
                    modifier = Modifier.semantics {
                        contentDescription = "Include tax in the total"
                    }
                )
            }
        }
        if (viewModel.taxEnabled) {
            Spacer(Modifier.size(8.dp))
            OutlinedTextField(
                value = viewModel.taxText,
                onValueChange = { new ->
                    if (new.isEmpty() || new.matches(Regex("^\\d*[.,]?\\d{0,2}$"))) {
                        viewModel.taxText = new
                    }
                },
                singleLine = true,
                label = { Text("Tax Rate") },
                suffix = { Text("%") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                modifier = Modifier
                    .fillMaxWidth()
                    .semantics { contentDescription = "Tax rate percentage" }
            )
        }
    }
}

/** Number-of-people stepper — 1 to 20, default 2 (spec component). */
@Composable
fun PeopleStepperCard(viewModel: CalculatorViewModel) {
    SectionCard {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    "People",
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    "${viewModel.people}",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold
                )
            }
            Row(verticalAlignment = Alignment.CenterVertically) {
                IconButton(
                    onClick = { viewModel.decrementPeople() },
                    enabled = viewModel.people > viewModel.minPeople
                ) {
                    Icon(Icons.Filled.Remove, contentDescription = "Remove a person")
                }
                Text(
                    "${viewModel.people}",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                IconButton(
                    onClick = { viewModel.incrementPeople() },
                    enabled = viewModel.people < viewModel.maxPeople
                ) {
                    Icon(Icons.Filled.Add, contentDescription = "Add a person")
                }
            }
        }
    }
}

/** Equal / Unequal split toggle (spec component). */
@Composable
fun SplitModeToggle(viewModel: CalculatorViewModel) {
    val haptics = LocalHapticFeedback.current
    SingleChoiceSegmentedButtonRow(modifier = Modifier.fillMaxWidth()) {
        SegmentedButton(
            selected = !viewModel.isUnequalSplit,
            onClick = {
                haptics.tap()
                viewModel.isUnequalSplit = false
            },
            shape = SegmentedButtonDefaults.itemShape(index = 0, count = 2)
        ) { Text("Equal Split") }
        SegmentedButton(
            selected = viewModel.isUnequalSplit,
            onClick = {
                haptics.tap()
                viewModel.isUnequalSplit = true
                viewModel.syncWeights()
            },
            shape = SegmentedButtonDefaults.itemShape(index = 1, count = 2)
        ) { Text("Unequal Split") }
    }
}

/** Round up / down / exact segmented control (spec component). */
@Composable
fun RoundingControlCard(viewModel: CalculatorViewModel) {
    val haptics = LocalHapticFeedback.current
    SectionCard {
        Text(
            "Rounding",
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(Modifier.size(8.dp))
        SingleChoiceSegmentedButtonRow(modifier = Modifier.fillMaxWidth()) {
            Rounding.entries.forEachIndexed { index, mode ->
                SegmentedButton(
                    selected = viewModel.rounding == mode,
                    onClick = {
                        haptics.tap()
                        viewModel.rounding = mode
                    },
                    shape = SegmentedButtonDefaults.itemShape(
                        index = index,
                        count = Rounding.entries.size
                    )
                ) { Text(mode.label) }
            }
        }
    }
}

/** Editor for unequal splits — assigns a weight per person (spec feature). */
@Composable
fun UnequalSplitEditor(viewModel: CalculatorViewModel) {
    val haptics = LocalHapticFeedback.current
    SectionCard {
        Text(
            "Shares per Person",
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            "Give whoever ordered more a higher share.",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(Modifier.size(8.dp))
        for (index in 0 until viewModel.people) {
            val weight = viewModel.customWeights.getOrElse(index) { 1f }
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 2.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    "Person ${index + 1}",
                    style = MaterialTheme.typography.bodyMedium
                )
                Row(verticalAlignment = Alignment.CenterVertically) {
                    IconButton(
                        onClick = {
                            haptics.tap()
                            viewModel.setWeight(index, weight - 1f)
                        },
                        enabled = weight > 0f
                    ) {
                        Icon(Icons.Filled.Remove, contentDescription = "Decrease share for person ${index + 1}")
                    }
                    Text(
                        "${weight.roundToInt()}x",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    IconButton(
                        onClick = {
                            haptics.tap()
                            viewModel.setWeight(index, weight + 1f)
                        },
                        enabled = weight < 20f
                    ) {
                        Icon(Icons.Filled.Add, contentDescription = "Increase share for person ${index + 1}")
                    }
                    Spacer(Modifier.width(8.dp))
                    Text(
                        CurrencyFormatter.string(viewModel.unequalShare(index)),
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.tertiary
                    )
                }
            }
        }
    }
}

/** Result card — per-person total, tip and tax (spec component). */
@Composable
fun ResultCard(viewModel: CalculatorViewModel) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primary
        ),
        shape = RoundedCornerShape(20.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                if (viewModel.isUnequalSplit) "Grand Total" else "Each Person Pays",
                style = MaterialTheme.typography.titleSmall,
                color = MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.85f)
            )
            Text(
                CurrencyFormatter.string(
                    if (viewModel.isUnequalSplit) viewModel.grandTotal
                    else viewModel.totalPerPerson
                ),
                fontSize = 40.sp,
                fontWeight = FontWeight.ExtraBold,
                color = MaterialTheme.colorScheme.onPrimary
            )
            Spacer(Modifier.size(4.dp))
            BreakdownRow("Bill", viewModel.billAmount)
            BreakdownRow("Tip (${viewModel.tipPercent.roundToInt()}%)", viewModel.tipAmount)
            if (viewModel.taxEnabled) {
                BreakdownRow("Tax", viewModel.taxAmount)
            }
            BreakdownRow("Grand Total", viewModel.grandTotal, emphasized = true)
            if (!viewModel.isUnequalSplit) {
                Spacer(Modifier.size(4.dp))
                BreakdownRow("Tip per Person", viewModel.tipPerPerson)
                if (viewModel.taxEnabled) {
                    BreakdownRow("Tax per Person", viewModel.taxPerPerson)
                }
                BreakdownRow("Total per Person", viewModel.totalPerPerson, emphasized = true)
            }
        }
    }
}

@Composable
private fun BreakdownRow(label: String, value: Double, emphasized: Boolean = false) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            label,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = if (emphasized) FontWeight.Bold else FontWeight.Normal,
            color = MaterialTheme.colorScheme.onPrimary.copy(
                alpha = if (emphasized) 1f else 0.85f
            )
        )
        Text(
            CurrencyFormatter.string(value),
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = if (emphasized) FontWeight.Bold else FontWeight.Medium,
            color = MaterialTheme.colorScheme.onPrimary
        )
    }
}

/** Shared rounded-surface card used by every input section. */
@Composable
fun SectionCard(content: @Composable () -> Unit) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f),
                shape = RoundedCornerShape(16.dp)
            )
            .padding(16.dp)
    ) {
        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) { content() }
    }
}
