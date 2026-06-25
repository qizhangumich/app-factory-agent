import SwiftUI
import Charts

/// A scrolling line chart of dB over time for the current session.
/// Uses Swift Charts, a system framework available on iOS 16+.
struct SessionChartView: View {
    var samples: [SessionSample]

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("chart.title")
                .font(.subheadline)
                .fontWeight(.semibold)
                .foregroundColor(.secondary)

            if samples.isEmpty {
                placeholder
            } else {
                chart
            }
        }
        .padding(14)
        .background(
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .fill(Color(.secondarySystemBackground))
        )
    }

    private var placeholder: some View {
        Text("chart.empty")
            .font(.footnote)
            .foregroundColor(.secondary)
            .frame(maxWidth: .infinity, minHeight: 120)
    }

    private var chart: some View {
        Chart(samples) { sample in
            AreaMark(
                x: .value("Time", sample.elapsed),
                y: .value("dB", sample.db)
            )
            .foregroundStyle(
                .linearGradient(
                    colors: [Color.teal.opacity(0.35), Color.teal.opacity(0.02)],
                    startPoint: .top,
                    endPoint: .bottom
                )
            )

            LineMark(
                x: .value("Time", sample.elapsed),
                y: .value("dB", sample.db)
            )
            .foregroundStyle(Color.teal)
            .interpolationMethod(.catmullRom)
        }
        .chartYScale(domain: 0...130)
        .chartYAxis {
            AxisMarks(values: [0, 40, 70, 85, 110, 130]) { value in
                AxisGridLine()
                AxisValueLabel {
                    if let v = value.as(Double.self) {
                        Text("\(Int(v))")
                    }
                }
            }
        }
        .chartXAxis {
            AxisMarks { value in
                AxisGridLine()
                AxisValueLabel {
                    if let secs = value.as(Double.self) {
                        Text(timeLabel(secs))
                    }
                }
            }
        }
        .frame(height: 140)
        .accessibilityLabel(Text("chart.title"))
    }

    /// Formats elapsed seconds as m:ss for the x-axis.
    private func timeLabel(_ seconds: Double) -> String {
        let total = Int(seconds.rounded())
        return String(format: "%d:%02d", total / 60, total % 60)
    }
}

#Preview {
    SessionChartView(samples: (0..<40).map {
        SessionSample(elapsed: Double($0) * 0.5,
                      db: 50 + 30 * Foundation.sin(Double($0) / 4))
    })
    .padding()
}
