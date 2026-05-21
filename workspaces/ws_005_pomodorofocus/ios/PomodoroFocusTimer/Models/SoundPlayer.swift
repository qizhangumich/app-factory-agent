//
//  SoundPlayer.swift
//  PomodoroFocusTimer
//
//  Optional focus sounds (tick / white noise / rain) via AVFoundation.
//
//  NOTE: audio asset files are not bundled in this code-only deliverable.
//  Drop `tick.caf`, `whitenoise.caf` and `rain.caf` into the app target and
//  this player loops them seamlessly. With no asset present the player
//  degrades gracefully to silent mode.
//

import AVFoundation

/// Plays a looping focus sound while a phase runs.
final class SoundPlayer {

    private var player: AVAudioPlayer?
    private var current: FocusSound = .silent

    /// File name (without extension) for each non-silent sound.
    private func assetName(for sound: FocusSound) -> String? {
        switch sound {
        case .silent:     return nil
        case .tick:       return "tick"
        case .whiteNoise: return "whitenoise"
        case .rain:       return "rain"
        }
    }

    /// Begins (or switches) playback for the given sound.
    func play(_ sound: FocusSound) {
        current = sound
        guard let name = assetName(for: sound) else {
            stop()
            return
        }
        // Already playing the requested sound — nothing to do.
        if player?.isPlaying == true, player?.url?.deletingPathExtension()
            .lastPathComponent == name {
            return
        }
        stop()
        guard let url = Self.locateAsset(named: name) else { return }
        configureSession()
        do {
            let p = try AVAudioPlayer(contentsOf: url)
            p.numberOfLoops = -1   // loop forever
            p.volume = 0.6
            p.prepareToPlay()
            p.play()
            player = p
        } catch {
            player = nil
        }
    }

    /// Resumes if a non-silent sound is selected (used on foreground return).
    func resumeIfNeeded(_ sound: FocusSound) {
        if current != .silent, player?.isPlaying == false {
            player?.play()
        } else if current == .silent {
            // selection changed to silent while away
        }
    }

    func pause() { player?.pause() }

    func stop() {
        player?.stop()
        player = nil
    }

    private func configureSession() {
        let session = AVAudioSession.sharedInstance()
        // .playback so loops continue while the screen locks / app backgrounds.
        try? session.setCategory(.playback, mode: .default, options: [.mixWithOthers])
        try? session.setActive(true)
    }

    /// Finds an audio asset, trying common loopable extensions.
    private static func locateAsset(named name: String) -> URL? {
        for ext in ["caf", "m4a", "mp3", "wav"] {
            if let url = Bundle.main.url(forResource: name, withExtension: ext) {
                return url
            }
        }
        return nil
    }
}
