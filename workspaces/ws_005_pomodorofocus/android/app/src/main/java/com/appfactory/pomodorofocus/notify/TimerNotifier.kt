package com.appfactory.pomodorofocus.notify

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.content.pm.PackageManager
import androidx.core.app.NotificationManagerCompat
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.workDataOf
import com.appfactory.pomodorofocus.R
import com.appfactory.pomodorofocus.model.PomodoroPhase
import java.util.concurrent.TimeUnit

/**
 * Schedules the single "timer finished" notification.
 *
 * BACKGROUND-SAFE DESIGN (per spec.technical_notes): the app never relies on
 * an in-process timer to alert the user. Instead a [TimerEndWorker] is
 * enqueued with WorkManager for the exact moment the phase ends, so the
 * notification fires even if the app process is dead. On pause / reset / skip
 * the worker is cancelled and re-enqueued.
 */
object TimerNotifier {

    const val CHANNEL_ID = "pomodoro_timer"
    const val NOTIFICATION_ID = 1001
    private const val WORK_NAME = "pomodoro_timer_end"

    /** Creates the notification channel. Safe to call repeatedly. */
    fun ensureChannel(context: Context) {
        val manager = context.getSystemService(NotificationManager::class.java)
        if (manager.getNotificationChannel(CHANNEL_ID) == null) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                context.getString(R.string.notif_channel_name),
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = context.getString(R.string.notif_channel_desc)
                enableVibration(true)
            }
            manager.createNotificationChannel(channel)
        }
    }

    /**
     * Enqueues a worker to post the timer-end notification after [delaySeconds].
     * @param endingPhase the phase that is ending — selects the message text.
     */
    fun scheduleTimerEnd(context: Context, delaySeconds: Long, endingPhase: PomodoroPhase) {
        cancelTimerEnd(context)
        if (delaySeconds <= 0) return
        val request = OneTimeWorkRequestBuilder<TimerEndWorker>()
            .setInitialDelay(delaySeconds, TimeUnit.SECONDS)
            .setInputData(workDataOf(TimerEndWorker.KEY_PHASE to endingPhase.storageValue))
            .build()
        WorkManager.getInstance(context).enqueueUniqueWork(
            WORK_NAME,
            androidx.work.ExistingWorkPolicy.REPLACE,
            request
        )
    }

    /** Cancels any pending timer-end notification (pause / reset / skip). */
    fun cancelTimerEnd(context: Context) {
        WorkManager.getInstance(context).cancelUniqueWork(WORK_NAME)
        NotificationManagerCompat.from(context).cancel(NOTIFICATION_ID)
    }

    /** Posts the notification immediately (called from [TimerEndWorker]). */
    fun postTimerEnd(context: Context, endingPhase: PomodoroPhase) {
        ensureChannel(context)
        val (titleRes, bodyRes) = when (endingPhase) {
            PomodoroPhase.FOCUS ->
                R.string.notif_focus_title to R.string.notif_focus_body
            else ->
                R.string.notif_break_title to R.string.notif_break_body
        }
        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_stat_timer)
            .setContentTitle(context.getString(titleRes))
            .setContentText(context.getString(bodyRes))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setAutoCancel(true)
            .build()

        // POST_NOTIFICATIONS is a runtime permission on Android 13+.
        if (ContextCompat.checkSelfPermission(
                context, Manifest.permission.POST_NOTIFICATIONS
            ) == PackageManager.PERMISSION_GRANTED
        ) {
            NotificationManagerCompat.from(context).notify(NOTIFICATION_ID, notification)
        }
    }
}
