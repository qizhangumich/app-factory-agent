import SwiftUI

/// The single-screen app: gauge, digital readout, color indicator, stats,
/// NIOSH exposure warning, session chart, calibration and pause/resume.
struct MeterView: View {
    @StateObject private var meter = AudioMeter()
    @Environment(\.scenePhase) private var scenePhase
    @State private var showCalibration = false

    /// Current safety classification of the live reading.
    private var level: NoiseLevel { NoiseLevel(db: meter.currentDB) }

    var body: some View {
        Group {
            if meter.permission == .denied {
                PermissionDeniedView()
            } else {
                meterContent
            }
        }
        .onAppear { meter.start() }
        .onDisappear { meter.teardown() }
        .onChange(of: scenePhase) { phase in
            // Stop sampling in the background; resume when active.
            switch phase {
            case .active:
                if meter.permission != .denied { meter.start() }
            case .background, .inactive:
                meter.pause()
            @unknown default:
                break
            }
        }
        .sheet(isPresented: $showCalibration) {
            CalibrationView(meter: meter)
        }
    }

    // MARK: Content

    private var meterContent: some View {
        ScrollView {
            VStack(spacing: 18) {
                gaugeSection
                colorIndicator
                exposureWarning
                StatsRowView(min: meter.minDB,
                             max: meter.maxDB,
                             avg: meter.averageDB,
                             peak: meter.peakDB,
                             onReset: meter.resetStats)
                SessionChartView(samples: meter.samples)
                controls
                disclaimer
            }
            .padding(.horizontal, 16)
            .padding(.bottom, 24)
        }
        .background(Color(.systemBackground))
        .navigationTitle("")
        .safeAreaInset(edge: .top) { header }
    }

    private var header: some View {
        HStack {
            Image(systemName: "waveform")
                .foregroundStyle(.tint)
            Text("app.name")
                .font(.headline)
            Spacer()
            Button {
                showCalibration = true
            } label: {
                Image(systemName: "slider.horizontal.3")
                    .font(.body)
            }
            .accessibilityLabel(Text("calibration.title"))
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(.bar)
    }

    // MARK: Gauge + readout

    private var gaugeSection: some View {
        ZStack(alignment: .bottom) {
            GaugeView(db: meter.currentDB, peak: meter.peakDB)
                .frame(height: 220)

            VStack(spacing: 0) {
                Text("\(Int(meter.currentDB.rounded()))")
                    .font(.system(size: 64, weight: .heavy, design: .rounded))
                    .monospacedDigit()
                    .foregroundColor(level.color)
                    .contentTransition(.numericText())
                Text("dB")
                    .font(.title3)
                    .fontWeight(.semibold)
                    .foregroundColor(.secondary)
                    .offset(y: -6)
            }
            .padding(.bottom, 4)
            .accessibilityElement(children: .combine)
            .accessibilityLabel(Text("readout.accessibility"))
            .accessibilityValue(Text("\(Int(meter.currentDB.rounded())) dB"))
        }
        .padding(.top, 8)
    }

    // MARK: Color indicator bar

    private var colorIndicator: some View {
        HStack(spacing: 10) {
            Circle()
                .fill(level.color)
                .frame(width: 14, height: 14)
            Text(level.labelKey)
                .font(.subheadline)
                .fontWeight(.semibold)
            Spacer()
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 10)
        .background(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(level.color.opacity(0.15))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(level.color.opacity(0.5), lineWidth: 1)
        )
        .accessibilityElement(children: .combine)
    }

    // MARK: NIOSH exposure warning

    private var exposureWarning: some View {
        HStack(spacing: 10) {
            Image(systemName: meter.currentDB > NoiseExposure.referenceDB
                  ? "exclamationmark.triangle.fill"
                  : "checkmark.shield.fill")
                .foregroundColor(meter.currentDB > NoiseExposure.referenceDB
                                 ? NoiseLevel.danger.color
                                 : NoiseLevel.safe.color)
            VStack(alignment: .leading, spacing: 2) {
                Text("exposure.heading")
                    .font(.caption2)
                    .fontWeight(.semibold)
                    .foregroundColor(.secondary)
                Text(NoiseExposure.guidance(forDB: meter.currentDB))
                    .font(.subheadline)
                    .fontWeight(.medium)
            }
            Spacer()
        }
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(Color(.secondarySystemBackground))
        )
        .accessibilityElement(children: .combine)
    }

    // MARK: Controls

    private var controls: some View {
        Button {
            if meter.isRunning {
                meter.pause()
            } else {
                meter.start()
            }
        } label: {
            Label(meter.isRunning ? "control.pause" : "control.resume",
                  systemImage: meter.isRunning ? "pause.fill" : "play.fill")
                .fontWeight(.semibold)
                .frame(maxWidth: .infinity)
        }
        .buttonStyle(.borderedProminent)
        .controlSize(.large)
        .tint(meter.isRunning ? NoiseLevel.danger.color : Color.teal)
    }

    private var disclaimer: some View {
        Text("disclaimer.body")
            .font(.caption2)
            .foregroundColor(.secondary)
            .multilineTextAlignment(.center)
            .padding(.horizontal, 8)
    }
}

#Preview {
    MeterView()
}
