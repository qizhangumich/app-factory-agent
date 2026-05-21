package com.appfactory.tipcalcdeluxe.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.unit.dp
import com.appfactory.tipcalcdeluxe.model.CalculatorViewModel
import com.appfactory.tipcalcdeluxe.model.HistoryStore
import com.appfactory.tipcalcdeluxe.util.tap

/**
 * The single screen of the app (spec.ui_spec screen "MainCalculator").
 * Bill input at top, controls in the middle, result card at the bottom.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainCalculatorScreen(
    viewModel: CalculatorViewModel,
    history: HistoryStore
) {
    val haptics = LocalHapticFeedback.current
    val scope = rememberCoroutineScope()
    var showHistory by remember { mutableStateOf(false) }
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)

    LaunchedEffect(Unit) { viewModel.syncWeights() }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Tip Calculator") },
                navigationIcon = {
                    IconButton(onClick = {
                        haptics.tap()
                        viewModel.reset()
                    }) {
                        Icon(Icons.Filled.Refresh, contentDescription = "Reset calculator")
                    }
                },
                actions = {
                    IconButton(onClick = {
                        haptics.tap()
                        showHistory = true
                    }) {
                        Icon(Icons.Filled.History, contentDescription = "Calculation history")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            BillAmountField(viewModel)
            TipSliderCard(viewModel)
            TaxControlCard(viewModel)
            PeopleStepperCard(viewModel)
            SplitModeToggle(viewModel)

            if (viewModel.isUnequalSplit && viewModel.people > 1) {
                UnequalSplitEditor(viewModel)
            }

            RoundingControlCard(viewModel)
            ResultCard(viewModel)
            SaveButton(viewModel, history)
        }
    }

    if (showHistory) {
        ModalBottomSheet(
            onDismissRequest = { showHistory = false },
            sheetState = sheetState
        ) {
            HistorySheetContent(
                history = history,
                onSelect = { entry ->
                    viewModel.restore(entry)
                    haptics.tap()
                    showHistory = false
                }
            )
        }
    }
}
