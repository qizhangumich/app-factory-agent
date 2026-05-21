package com.appfactory.pomodorofocus.data

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

/** The app's single Room database, holding completed Pomodoro sessions. */
@Database(entities = [Session::class], version = 1, exportSchema = true)
abstract class PomodoroDatabase : RoomDatabase() {

    abstract fun sessionDao(): SessionDao

    companion object {
        @Volatile
        private var INSTANCE: PomodoroDatabase? = null

        /** Returns the process-wide singleton database instance. */
        fun get(context: Context): PomodoroDatabase =
            INSTANCE ?: synchronized(this) {
                INSTANCE ?: Room.databaseBuilder(
                    context.applicationContext,
                    PomodoroDatabase::class.java,
                    "pomodoro.db"
                ).build().also { INSTANCE = it }
            }
    }
}
