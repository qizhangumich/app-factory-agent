import SwiftUI

/// The MIN | MAX | AVG | PEAK statistics row with a reset button.
struct StatsRowView: View {
    var min: Double
    var max: Double
    var avg: Double
    var peak: Double
    var onReset: () -> Void

    var body: some View {
        HStack(spacing: 0) {
            stat(titleKey: "stat.min", value: min)
            divider
            stat(titleKey: "stat.max", value: max)
            divider
            stat(titleKey: "stat.avg", value: avg)
            divider
            stat(titleKey: "stat.peak", value: peak)
        }
        .padding(.vertical, 12)
        .background(
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .fill(Color(.secondarySystemBackground))
        )
        .overlay(alignment: .topTrailing) {
            Button(action: onReset) {
                Image(systemName: "arrow.counterclockwise.circle.fill")
                    .font(.title3)
                    .foregroundStyle(.tint)
            }
            .padding(8)
            .accessibilityLabel(Text("stat.reset"))
        }
    }

    private var divider: some View {
        Rectangle()
            .fill(Color(.separator))
            .frame(width: 1, height: 32)
    }

    private func stat(titleKey: LocalizedStringKey, value: Double) -> some View {
        VStack(spacing: 4) {
            Text(titleKey)
                .font(.caption2)
                .fontWeight(.semibold)
                .foregroundColor(.secondary)
            Text("\(Int(value.rounded()))")
                .font(.system(size: 22, weight: .bold, design: .rounded))
                .monospacedDigit()
            Text("dB")
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .accessibilityElement(children: .combine)
    }
}

#Preview {
    StatsRowView(min: 38, max: 102, avg: 64, peak: 108, onReset: {})
        .padding()
}
