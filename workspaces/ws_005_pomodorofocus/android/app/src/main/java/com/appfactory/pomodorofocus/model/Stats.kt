package com.appfactory.pomodorofocus.model

import com.appfactory.pomodorofocus.data.Session
import java.util.Calendar

/** Aggregated focus figures for one calendar day (used by the heat map). */
data class DayStats(
    val dayStartMillis: Long,
    val focusSessions: Int,
    val focusMinutes: Int
)

/** Bundle of every figure shown on the Stats screen. */
data class StatsSummary(
    val todaySessions: Int,
    val todayMinutes: Int,
    val weekSessions: Int,
    val weekMinutes: Int,
    val weekDailyAverage: Int,
    val monthSessions: Int,
    val monthMinutes: Int,
    val allTimeSessions: Int,
    val allTimeMinutes: Int,
    val currentStreak: Int,
    val bestStreak: Int,
    val heatMap: List<DayStats>
)

/**
 * Pure statistics engine — turns a list of [Session]s into a [StatsSummary].
 * Stateless so it is trivial to unit-test.
 */
object StatsCalculator {

    private const val DAY_MS = 24L * 60 * 60 * 1000

    private fun startOfDay(millis: Long): Long {
        val cal = Calendar.getInstance()
        cal.timeInMillis = millis
        cal.set(Calendar.HOUR_OF_DAY, 0)
        cal.set(Calendar.MINUTE, 0)
        cal.set(Calendar.SECOND, 0)
        cal.set(Calendar.MILLISECOND, 0)
        return cal.timeInMillis
    }

    /** Builds the full summary for [sessions], evaluated relative to [now]. */
    fun summarize(
        sessions: List<Session>,
        now: Long = System.currentTimeMillis(),
        heatMapDays: Int = 90
    ): StatsSummary {
        val focus = sessions.filter { it.type == PomodoroPhase.FOCUS.storageValue }
        val today = startOfDay(now)
        val weekStart = today - 6 * DAY_MS
        val monthStart = today - 29 * DAY_MS

        val todayList = focus.filter { startOfDay(it.completedAt) == today }
        val weekList = focus.filter { it.completedAt >= weekStart }
        val monthList = focus.filter { it.completedAt >= monthStart }

        // Set of day-start millis that have at least one focus session.
        val focusDays = focus.map { startOfDay(it.completedAt) }.toSet()

        return StatsSummary(
            todaySessions = todayList.size,
            todayMinutes = todayList.sumOf { it.minutes },
            weekSessions = weekList.size,
            weekMinutes = weekList.sumOf { it.minutes },
            weekDailyAverage = weekList.sumOf { it.minutes } / 7,
            monthSessions = monthList.size,
            monthMinutes = monthList.sumOf { it.minutes },
            allTimeSessions = focus.size,
            allTimeMinutes = focus.sumOf { it.minutes },
            currentStreak = currentStreak(focusDays, today),
            bestStreak = bestStreak(focusDays),
            heatMap = heatMap(focus, today, heatMapDays)
        )
    }

    /** Consecutive days (ending today or yesterday) with >=1 focus session. */
    private fun currentStreak(focusDays: Set<Long>, today: Long): Int {
        if (focusDays.isEmpty()) return 0
        var cursor = today
        if (!focusDays.contains(cursor)) {
            // Streak is still alive if yesterday had a session.
            cursor -= DAY_MS
            if (!focusDays.contains(cursor)) return 0
        }
        var streak = 0
        while (focusDays.contains(cursor)) {
            streak++
            cursor -= DAY_MS
        }
        return streak
    }

    /** Longest run of consecutive focus days ever. */
    private fun bestStreak(focusDays: Set<Long>): Int {
        if (focusDays.isEmpty()) return 0
        val sorted = focusDays.sorted()
        var best = 1
        var run = 1
        for (i in 1 until sorted.size) {
            if (sorted[i] - sorted[i - 1] == DAY_MS) {
                run++
                best = maxOf(best, run)
            } else {
                run = 1
            }
        }
        return best
    }

    /** Oldest-first [dayCount]-day window for the contribution heat map. */
    private fun heatMap(focus: List<Session>, today: Long, dayCount: Int): List<DayStats> {
        val byDay = focus.groupBy { startOfDay(it.completedAt) }
        return (dayCount - 1 downTo 0).map { offset ->
            val day = today - offset * DAY_MS
            val items = byDay[day].orEmpty()
            DayStats(
                dayStartMillis = day,
                focusSessions = items.size,
                focusMinutes = items.sumOf { it.minutes }
            )
        }
    }
}
