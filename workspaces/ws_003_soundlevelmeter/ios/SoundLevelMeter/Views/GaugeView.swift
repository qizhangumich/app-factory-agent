import SwiftUI

/// A semicircular analog gauge (0–130 dB) drawn with SwiftUI `Canvas`.
///
/// The arc spans 180° (from 9 o'clock, sweeping over the top, to 3 o'clock).
/// Colored band segments mark the safe / moderate / danger ranges, tick marks
/// and labels are drawn around the arc, and an animated needle points at the
/// current value.
struct GaugeView: View {
    /// Current sound level in dB.
    var db: Double
    /// Peak level, drawn as a thin marker on the arc.
    var peak: Double

    private let minDB = NoiseLevel.minDB        // 0
    private let maxDB = NoiseLevel.maxDB        // 130
    /// Start / end angles for a top semicircle. 180° = left, 360° = right.
    private let startAngle: Double = 180
    private let endAngle: Double = 360

    var body: some View {
        Canvas { context, size in
            let radius = min(size.width / 2, size.height) - 24
            let center = CGPoint(x: size.width / 2, y: size.height - 12)

            drawColorBands(context: context, center: center, radius: radius)
            drawTicks(context: context, center: center, radius: radius)
            drawPeakMarker(context: context, center: center, radius: radius)
            drawNeedle(context: context, center: center, radius: radius)
            drawHub(context: context, center: center)
        }
        .animation(.spring(response: 0.35, dampingFraction: 0.7), value: db)
        .accessibilityElement()
        .accessibilityLabel(Text("gauge.accessibility"))
        .accessibilityValue(Text("\(Int(db.rounded())) dB"))
    }

    // MARK: Angle helpers

    /// Maps a dB value to a gauge angle in degrees.
    private func angle(for value: Double) -> Double {
        let clamped = min(max(value, minDB), maxDB)
        let fraction = (clamped - minDB) / (maxDB - minDB)
        return startAngle + fraction * (endAngle - startAngle)
    }

    private func point(center: CGPoint, radius: CGFloat, degrees: Double) -> CGPoint {
        let rad = degrees * .pi / 180
        return CGPoint(x: center.x + radius * cos(rad),
                       y: center.y + radius * sin(rad))
    }

    // MARK: Drawing

    private func drawColorBands(context: GraphicsContext, center: CGPoint, radius: CGFloat) {
        // (lowerDB, upperDB, color) for each safety band.
        let bands: [(Double, Double, Color)] = [
            (0, 70, NoiseLevel.safe.color),
            (70, 85, NoiseLevel.moderate.color),
            (85, 130, NoiseLevel.danger.color)
        ]
        let lineWidth: CGFloat = 14
        for band in bands {
            var path = Path()
            path.addArc(center: center,
                        radius: radius,
                        startAngle: .degrees(angle(for: band.0)),
                        endAngle: .degrees(angle(for: band.1)),
                        clockwise: false)
            context.stroke(path, with: .color(band.2.opacity(0.85)),
                           style: StrokeStyle(lineWidth: lineWidth, lineCap: .butt))
        }
    }

    private func drawTicks(context: GraphicsContext, center: CGPoint, radius: CGFloat) {
        // Major ticks every 10 dB with numeric labels.
        for value in stride(from: 0.0, through: 130.0, by: 10.0) {
            let deg = angle(for: value)
            let outer = point(center: center, radius: radius - 22, degrees: deg)
            let inner = point(center: center, radius: radius - 32, degrees: deg)
            var tick = Path()
            tick.move(to: inner)
            tick.addLine(to: outer)
            context.stroke(tick, with: .color(.secondary),
                           style: StrokeStyle(lineWidth: 2, lineCap: .round))

            let labelPoint = point(center: center, radius: radius - 46, degrees: deg)
            let text = Text("\(Int(value))")
                .font(.system(size: 11, weight: .medium))
                .foregroundColor(.secondary)
            context.draw(text, at: labelPoint)
        }
    }

    private func drawPeakMarker(context: GraphicsContext, center: CGPoint, radius: CGFloat) {
        guard peak > minDB else { return }
        let deg = angle(for: peak)
        let outer = point(center: center, radius: radius + 8, degrees: deg)
        let inner = point(center: center, radius: radius - 8, degrees: deg)
        var marker = Path()
        marker.move(to: inner)
        marker.addLine(to: outer)
        context.stroke(marker, with: .color(.primary),
                       style: StrokeStyle(lineWidth: 3, lineCap: .round))
    }

    private func drawNeedle(context: GraphicsContext, center: CGPoint, radius: CGFloat) {
        let deg = angle(for: db)
        let tip = point(center: center, radius: radius - 4, degrees: deg)
        // A short tail behind the hub for an analog look.
        let tail = point(center: center, radius: -18, degrees: deg)

        var needle = Path()
        needle.move(to: tail)
        needle.addLine(to: tip)
        context.stroke(needle,
                       with: .color(NoiseLevel(db: db).color),
                       style: StrokeStyle(lineWidth: 4, lineCap: .round))
    }

    private func drawHub(context: GraphicsContext, center: CGPoint) {
        let hub = Path(ellipseIn: CGRect(x: center.x - 10, y: center.y - 10,
                                         width: 20, height: 20))
        context.fill(hub, with: .color(.primary))
        let inner = Path(ellipseIn: CGRect(x: center.x - 4, y: center.y - 4,
                                           width: 8, height: 8))
        context.fill(inner, with: .color(NoiseLevel(db: db).color))
    }
}

#Preview {
    GaugeView(db: 72, peak: 96)
        .frame(height: 240)
        .padding()
}
