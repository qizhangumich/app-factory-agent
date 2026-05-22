package com.appfactory.pomodorofocus.ui

import androidx.compose.foundation.background
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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyHorizontalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CalendarMonth
import androidx.compose.material.icons.filled.EmojiEvents
import androidx.compose.material.icons.filled.GridView
import androidx.compose.material.icons.filled.LocalFireDepartment
import androidx.compose.material.icons.filled.WbSunny
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.appfactory.pomodorofocus.R
import com.appfactory.pomodorofocus.TimerViewModel
import com.appfactory.pomodorofocus.model.DayStats
import com.appfactory.pomodorofocus.model.StatsSummary

/** Statistics screen: 90-day heat map, streaks and metric cards. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StatsScreen(viewModel: TimerViewModel, modifier: Modifier = Modifier) {
    val stats by viewModel.stats.collectAsState()

    Column(modifier = modifier.fillMaxSize()) {
        TopAppBar(title = { Text(stringResource(R.string.tab_stats)) })

        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
            contentPadding = androidx.compose.foundation.layout.PaddingValues(vertical = 12.dp)
        ) {
            item { HeatMapCard(stats) }
            item { StreakRow(stats) }
            item { TodayCard(stats) }
            item { WeekCard(stats) }
            item { MonthCard(stats) }
            item { AllTimeCard(stats) }
        }
    }
}

/** GitHub-style 90-day contribution heat map. */
@Composable
private fun HeatMapCard(stats: StatsSummary) {
    StatCard(
        title = stringResource(R.string.stats_heatmap),
        icon = Icons.Default.GridView,
        accent = Color(0xFF4FBF4F)
    ) {
        LazyHorizontalGrid(
            rows = GridCells.Fixed(7),
            modifier = Modifier
                .fillMaxWidth()
                .height(17.dp * 7),
            horizontalArrangement = Arrangement.spacedBy(3.dp),
            verticalArrangement = Arrangement.spacedBy(3.dp)
        ) {
            items(stats.heatMap) { day ->
                Box(
                    modifier = Modifier
                        .size(14.dp)
                        .clip(RoundedCornerShape(3.dp))
                        .background(heatColor(day))
                )
            }
        }
        Spacer(Modifier.height(8.dp))
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(
                stringResource(R.string.stats_less),
                fontSize = 11.sp,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
            )
            (0..4).forEach { level ->
                Box(
                    modifier = Modifier
                        .size(11.dp)
                        .clip(RoundedCornerShape(2.dp))
                        .background(heatColorForLevel(level))
                )
            }
            Text(
                stringResource(R.string.stats_more),
                fontSize = 11.sp,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
            )
        }
    }
}

private fun heatColor(day: DayStats): Color = heatColorForLevel(
    when (day.focusSessions) {
        0 -> 0
        1 -> 1
        in 2..3 -> 2
        in 4..5 -> 3
        else -> 4
    }
)

private fun heatColorForLevel(level: Int): Color = when (level) {
    0 -> Color.White.copy(alpha = 0.08f)
    1 -> Color(0xFF2E5E2E)
    2 -> Color(0xFF3B8C3B)
    3 -> Color(0xFF4FBF4F)
    else -> Color(0xFF6BE86B)
}

@Composable
private fun StreakRow(stats: StatsSummary) {
    Row(horizontalArrangement = Arrangement.spacedBy(14.dp)) {
        StatCard(
            title = stringResource(R.string.stats_current_streak),
            icon = Icons.Default.LocalFireDepartment,
            accent = Color(0xFFFF6B6B),
            modifier = Modifier.weight(1f)
        ) {
            Metric(
                value = stringResource(R.string.stats_day_value, stats.currentStreak),
                caption = stringResource(R.string.stats_consecutive_days)
            )
        }
        StatCard(
            title = stringResource(R.string.stats_best_streak),
            icon = Icons.Default.EmojiEvents,
            accent = Color(0xFF45B7D1),
            modifier = Modifier.weight(1f)
        ) {
            Metric(
                value = stringResource(R.string.stats_day_value, stats.bestStreak),
                caption = stringResource(R.string.stats_longest_run)
            )
        }
    }
}

@Composable
private fun TodayCard(stats: StatsSummary) {
    StatCard(
        title = stringResource(R.string.stats_today),
        icon = Icons.Default.WbSunny,
        accent = Color(0xFFFF6B6B)
    ) {
        Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween) {
            Metric("${stats.todaySessions}", stringResource(R.string.stats_sessions))
            Metric("${stats.todayMinutes}", stringResource(R.string.stats_focus_minutes))
        }
    }
}

@Composable
private fun WeekCard(stats: StatsSummary) {
    StatCard(
        title = stringResource(R.string.stats_this_week),
        icon = Icons.Default.CalendarMonth,
        accent = Color(0xFF4ECDC4)
    ) {
        Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween) {
            Metric("${stats.weekSessions}", stringResource(R.string.stats_sessions))
            Metric("${stats.weekMinutes}", stringResource(R.string.stats_focus_minutes))
            Metric("${stats.weekDailyAverage}", stringResource(R.string.stats_daily_avg))
        }
    }
}

@Composable
private fun MonthCard(stats: StatsSummary) {
    StatCard(
        title = stringResource(R.string.stats_this_month),
        icon = Icons.Default.CalendarMonth,
        accent = Color(0xFF45B7D1)
    ) {
        Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween) {
            Metric("${stats.monthSessions}", stringResource(R.string.stats_sessions))
            Metric("${stats.monthMinutes}", stringResource(R.string.stats_focus_minutes))
        }
    }
}

@Composable
private fun AllTimeCard(stats: StatsSummary) {
    StatCard(
        title = stringResource(R.string.stats_all_time),
        icon = Icons.Default.EmojiEvents,
        accent = Color(0xFF9B8CFF)
    ) {
        Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween) {
            Metric("${stats.allTimeSessions}", stringResource(R.string.stats_sessions))
            Metric("${stats.allTimeMinutes}", stringResource(R.string.stats_focus_minutes))
        }
    }
}

/** Rounded card used for every statistic block. */
@Composable
private fun StatCard(
    title: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    accent: Color,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(icon, contentDescription = null, tint = accent)
                Spacer(Modifier.width(8.dp))
                Text(title, color = accent, fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
            }
            content()
        }
    }
}

/** Big-number + caption metric. */
@Composable
private fun Metric(value: String, caption: String) {
    Column {
        Text(value, fontSize = 26.sp, fontWeight = FontWeight.Bold)
        Text(
            caption,
            fontSize = 12.sp,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.65f)
        )
    }
}
