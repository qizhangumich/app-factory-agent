package com.appfactory.pomodorofocus.data

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.UUID

/**
 * A completed Pomodoro session.
 *
 * Data model (per spec): Session(id, date, type, durationSeconds, completedAt).
 *
 * - [date] is the start-of-day epoch millis for the day the session belongs to,
 *   used to group sessions for the statistics queries.
 * - [completedAt] is the exact epoch-millis timestamp the session finished.
 * - [type] is one of "focus" / "short" / "long".
 */
@Entity(tableName = "sessions")
data class Session(
    @PrimaryKey
    val id: String = UUID.randomUUID().toString(),
    val date: Long,
    val type: String,
    val durationSeconds: Int,
    val completedAt: Long
) {
    /** Whole minutes of the session. */
    val minutes: Int get() = durationSeconds / 60
}
