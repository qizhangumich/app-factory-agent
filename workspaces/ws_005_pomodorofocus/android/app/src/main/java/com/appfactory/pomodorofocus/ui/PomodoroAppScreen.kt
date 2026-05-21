package com.appfactory.pomodorofocus.ui

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.BarChart
import androidx.compose.material.icons.filled.Timer
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import com.appfactory.pomodorofocus.R
import com.appfactory.pomodorofocus.TimerViewModel

/** Top-level scaffold with a Timer / Stats bottom navigation bar. */
@Composable
fun PomodoroAppScreen(viewModel: TimerViewModel) {
    var selectedTab by rememberSaveable { mutableIntStateOf(0) }

    Scaffold(
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    icon = { Icon(Icons.Default.Timer, contentDescription = null) },
                    label = { Text(stringResource(R.string.tab_timer)) }
                )
                NavigationBarItem(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    icon = { Icon(Icons.Default.BarChart, contentDescription = null) },
                    label = { Text(stringResource(R.string.tab_stats)) }
                )
            }
        }
    ) { innerPadding ->
        when (selectedTab) {
            0 -> TimerScreen(viewModel, Modifier.padding(innerPadding))
            else -> StatsScreen(viewModel, Modifier.padding(innerPadding))
        }
    }
}
