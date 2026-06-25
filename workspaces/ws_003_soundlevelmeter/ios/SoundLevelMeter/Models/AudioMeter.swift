import Foundation
import AVFoundation
import Combine

/// Wraps `AVAudioRecorder` metering to produce a real-time sound-level reading.
///
/// The recorder writes to a throw-away file in the temporary directory; nothing
/// is ever persisted or transmitted — the file exists only so the metering API
/// has a sink, and it is removed when measurement stops.
///
/// dB conversion (per spec.technical_notes): `averagePowerForChannel` returns a
/// value in dBFS roughly in the range -160...0. We map that to an approximate
/// dB SPL value by adding a fixed offset (160) plus the user calibration offset.
/// iPhone microphones are not laboratory calibrated, so the readout is an
/// approximation — see the in-app disclaimer.
@MainActor
final class AudioMeter: NSObject, ObservableObject {

    // MARK: Permission state

    enum PermissionState {
        case unknown
        case granted
        case denied
    }

    // MARK: Published readout

    /// Current (smoothed) sound level in dB.
    @Published private(set) var currentDB: Double = 0
    /// Instantaneous peak level since last reset.
    @Published private(set) var peakDB: Double = 0
    @Published private(set) var minDB: Double = 0
    @Published private(set) var maxDB: Double = 0
    /// Running average of all samples since last reset.
    @Published private(set) var averageDB: Double = 0
    /// Time-series samples for the session chart.
    @Published private(set) var samples: [SessionSample] = []
    /// True while the meter is actively sampling.
    @Published private(set) var isRunning: Bool = false
    @Published private(set) var permission: PermissionState = .unknown

    /// User calibration offset in dB (±10), persisted in UserDefaults.
    @Published var calibrationOffset: Double {
        didSet {
            UserDefaults.standard.set(calibrationOffset, forKey: Self.calibrationKey)
        }
    }

    // MARK: Constants

    static let calibrationKey = "calibration_offset_db"
    /// Sampling rate: 10 Hz as specified.
    private static let sampleInterval: TimeInterval = 0.1
    /// Rough dBFS -> dB SPL offset.
    private static let splOffset: Double = 160
    /// Smoothing factor for the displayed needle value (0..1, higher = snappier).
    private static let smoothing: Double = 0.35
    /// Keep at most this many chart samples (~10 minutes at 10 Hz would be huge,
    /// so we down-sample the chart and cap memory).
    private static let maxSamples = 600

    // MARK: Private state

    private var recorder: AVAudioRecorder?
    private var timer: Timer?
    private var sampleCount: Int = 0
    private var dbSum: Double = 0
    private var sessionStart: Date?
    private var chartTick: Int = 0
    private let recordingURL: URL = {
        FileManager.default.temporaryDirectory
            .appendingPathComponent("slm_metering.caf")
    }()

    // MARK: Init

    override init() {
        let stored = UserDefaults.standard.object(forKey: Self.calibrationKey) as? Double
        self.calibrationOffset = stored ?? 0
        super.init()
    }

    // MARK: Permission

    /// Requests microphone access and updates `permission`.
    func requestPermission(completion: @escaping (Bool) -> Void) {
        let session = AVAudioSession.sharedInstance()
        switch session.recordPermission {
        case .granted:
            permission = .granted
            completion(true)
        case .denied:
            permission = .denied
            completion(false)
        case .undetermined:
            session.requestRecordPermission { [weak self] granted in
                DispatchQueue.main.async {
                    self?.permission = granted ? .granted : .denied
                    completion(granted)
                }
            }
        @unknown default:
            permission = .unknown
            completion(false)
        }
    }

    // MARK: Lifecycle

    /// Begins (or resumes) metering. Requests permission first if needed.
    func start() {
        guard !isRunning else { return }
        requestPermission { [weak self] granted in
            guard let self, granted else { return }
            self.beginRecording()
        }
    }

    /// Pauses metering without discarding accumulated stats / samples.
    func pause() {
        guard isRunning else { return }
        timer?.invalidate()
        timer = nil
        recorder?.stop()
        recorder = nil
        isRunning = false
        deactivateSession()
    }

    /// Resets all statistics and the session chart. Keeps running if active.
    func resetStats() {
        peakDB = 0
        minDB = currentDB
        maxDB = currentDB
        averageDB = currentDB
        dbSum = currentDB
        sampleCount = currentDB > 0 ? 1 : 0
        samples.removeAll()
        sessionStart = Date()
        chartTick = 0
    }

    /// Stops metering entirely and cleans up the scratch file.
    func teardown() {
        pause()
        try? FileManager.default.removeItem(at: recordingURL)
    }

    // MARK: Recording setup

    private func beginRecording() {
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(.playAndRecord,
                                    mode: .measurement,
                                    options: [.mixWithOthers])
            try session.setActive(true)

            let settings: [String: Any] = [
                AVFormatIDKey: Int(kAudioFormatLinearPCM),
                AVSampleRateKey: 44_100.0,
                AVNumberOfChannelsKey: 1,
                AVLinearPCMBitDepthKey: 16,
                AVLinearPCMIsBigEndianKey: false,
                AVLinearPCMIsFloatKey: false
            ]
            let rec = try AVAudioRecorder(url: recordingURL, settings: settings)
            rec.isMeteringEnabled = true
            rec.prepareToRecord()
            rec.record()
            recorder = rec

            if sessionStart == nil { sessionStart = Date() }
            isRunning = true
            startTimer()
        } catch {
            isRunning = false
        }
    }

    private func deactivateSession() {
        try? AVAudioSession.sharedInstance()
            .setActive(false, options: .notifyOthersOnDeactivation)
    }

    // MARK: Sampling

    private func startTimer() {
        timer?.invalidate()
        let t = Timer(timeInterval: Self.sampleInterval, repeats: true) { [weak self] _ in
            Task { @MainActor in self?.sample() }
        }
        RunLoop.main.add(t, forMode: .common)
        timer = t
    }

    private func sample() {
        guard let recorder, isRunning else { return }
        recorder.updateMeters()

        let power = Double(recorder.averagePower(forChannel: 0))
        let peakPower = Double(recorder.peakPower(forChannel: 0))

        let db = clampDB(power + Self.splOffset + calibrationOffset)
        let peak = clampDB(peakPower + Self.splOffset + calibrationOffset)

        // Smooth the displayed value so the needle moves naturally.
        currentDB = currentDB + (db - currentDB) * Self.smoothing

        // Statistics use the (smoothed) current value.
        let value = currentDB
        if sampleCount == 0 {
            minDB = value
            maxDB = value
        } else {
            minDB = Swift.min(minDB, value)
            maxDB = Swift.max(maxDB, value)
        }
        peakDB = Swift.max(peakDB, peak)
        dbSum += value
        sampleCount += 1
        averageDB = dbSum / Double(sampleCount)

        // Chart: append roughly every 0.5 s to keep the series readable.
        chartTick += 1
        if chartTick % 5 == 0 {
            let elapsed = Date().timeIntervalSince(sessionStart ?? Date())
            samples.append(SessionSample(elapsed: elapsed, db: value))
            if samples.count > Self.maxSamples {
                samples.removeFirst(samples.count - Self.maxSamples)
            }
        }
    }

    /// Clamps a dB value to the displayable gauge range.
    private func clampDB(_ value: Double) -> Double {
        Swift.min(Swift.max(value, NoiseLevel.minDB), NoiseLevel.maxDB)
    }
}
