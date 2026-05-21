package com.appfactory.pomodorofocus.audio

import android.content.Context
import android.media.AudioAttributes
import android.media.MediaPlayer
import com.appfactory.pomodorofocus.model.FocusSound

/**
 * Plays an optional looping focus sound while a phase runs.
 *
 * NOTE: audio assets are not bundled in this code-only deliverable. Drop
 * `tick.ogg`, `whitenoise.ogg` and `rain.ogg` into `app/src/main/res/raw/`
 * and this player loops them. With no asset present it degrades gracefully
 * to silent mode.
 */
class SoundPlayer(private val context: Context) {

    private var player: MediaPlayer? = null
    private var current: FocusSound = FocusSound.SILENT

    /** Resource name (without extension) expected in res/raw for each sound. */
    private fun rawName(sound: FocusSound): String? = when (sound) {
        FocusSound.SILENT -> null
        FocusSound.TICK -> "tick"
        FocusSound.WHITE_NOISE -> "whitenoise"
        FocusSound.RAIN -> "rain"
    }

    /** Starts (or switches to) the given looping sound. */
    fun play(sound: FocusSound) {
        if (sound == current && player?.isPlaying == true) return
        current = sound
        stop()
        val name = rawName(sound) ?: return
        val resId = context.resources.getIdentifier(name, "raw", context.packageName)
        if (resId == 0) return // asset not bundled — stay silent
        player = MediaPlayer.create(context, resId)?.apply {
            isLooping = true
            setAudioAttributes(
                AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_MEDIA)
                    .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                    .build()
            )
            setVolume(0.6f, 0.6f)
            start()
        }
    }

    /** Pauses playback, retaining position (used when the timer pauses). */
    fun pause() {
        player?.takeIf { it.isPlaying }?.pause()
    }

    /** Resumes a previously selected non-silent sound. */
    fun resume() {
        if (current != FocusSound.SILENT) {
            player?.takeIf { !it.isPlaying }?.start()
        }
    }

    /** Stops and releases the player. */
    fun stop() {
        player?.run {
            if (isPlaying) stop()
            release()
        }
        player = null
    }
}
