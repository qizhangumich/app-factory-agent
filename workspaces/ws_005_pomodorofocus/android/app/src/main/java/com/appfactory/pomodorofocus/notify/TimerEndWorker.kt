package com.appfactory.pomodorofocus.notify

import android.content.Context
import androidx.work.Worker
import androidx.work.WorkerParameters
import com.appfactory.pomodorofocus.model.PomodoroPhase

/**
 * WorkManager worker that posts the timer-end notification.
 *
 * Enqueued by [TimerNotifier.scheduleTimerEnd] with an initial delay equal to
 * the remaining phase time, so the alert fires at the exact end moment even
 * when the app process has been killed.
 */
class TimerEndWorker(
    context: Context,
    params: WorkerParameters
) : Worker(context, params) {

    override fun doWork(): Result {
        val phase = PomodoroPhase.fromStorage(
            inputData.getString(KEY_PHASE) ?: PomodoroPhase.FOCUS.storageValue
        )
        TimerNotifier.postTimerEnd(applicationContext, phase)
        return Result.success()
    }

    companion object {
        const val KEY_PHASE = "ending_phase"
    }
}
