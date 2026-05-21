package com.appfactory.pomodorofocus

import android.app.Application
import com.appfactory.pomodorofocus.notify.TimerNotifier

/** Application entry point — creates the notification channel up front. */
class PomodoroApp : Application() {
    override fun onCreate() {
        super.onCreate()
        TimerNotifier.ensureChannel(this)
    }
}
