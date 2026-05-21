package com.appfactory.pomodorofocus.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

/** Room data-access object for [Session] rows. */
@Dao
interface SessionDao {

    /** Inserts a finished session. */
    @Insert
    suspend fun insert(session: Session)

    /** Observes every session, newest first — drives all statistics screens. */
    @Query("SELECT * FROM sessions ORDER BY completedAt DESC")
    fun observeAll(): Flow<List<Session>>

    /** One-shot fetch of every session. */
    @Query("SELECT * FROM sessions ORDER BY completedAt DESC")
    suspend fun getAll(): List<Session>

    /** Deletes every recorded session (the "reset statistics" action). */
    @Query("DELETE FROM sessions")
    suspend fun deleteAll()
}
