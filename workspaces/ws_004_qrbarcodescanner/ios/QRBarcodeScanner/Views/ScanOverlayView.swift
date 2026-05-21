//
//  ScanOverlayView.swift
//  QRBarcodeScanner
//
//  The translucent scan-target reticle drawn over the camera preview.
//

import SwiftUI

/// A rounded scan-target rectangle with corner accents, centred on screen.
struct ScanOverlayView: View {

    /// True briefly after a successful scan to flash the reticle green.
    var didFlashSuccess: Bool

    private let cornerLength: CGFloat = 32
    private let lineWidth: CGFloat = 5

    var body: some View {
        GeometryReader { geo in
            let side = min(geo.size.width, geo.size.height) * 0.68
            let rect = CGRect(
                x: (geo.size.width - side) / 2,
                y: (geo.size.height - side) / 2,
                width: side,
                height: side)
            let color: Color = didFlashSuccess ? .scanSuccess : .white

            ZStack {
                // Dimmed mask everywhere except the scan window.
                Rectangle()
                    .fill(Color.black.opacity(0.45))
                    .mask(
                        Rectangle()
                            .overlay(
                                RoundedRectangle(cornerRadius: 24)
                                    .frame(width: side, height: side)
                                    .blendMode(.destinationOut)
                            )
                            .compositingGroup()
                    )

                // Subtle full border.
                RoundedRectangle(cornerRadius: 24)
                    .strokeBorder(color.opacity(0.5), lineWidth: 2)
                    .frame(width: side, height: side)

                // Bright corner accents.
                ForEach(Corner.allCases, id: \.self) { corner in
                    CornerShape(corner: corner, length: cornerLength)
                        .stroke(color,
                                style: StrokeStyle(lineWidth: lineWidth,
                                                   lineCap: .round))
                        .frame(width: side, height: side)
                }
            }
            .position(x: rect.midX, y: rect.midY)
            .animation(.easeInOut(duration: 0.2), value: didFlashSuccess)
            .accessibilityHidden(true)
        }
        .ignoresSafeArea()
    }
}

/// The four corners of the scan reticle.
private enum Corner: CaseIterable {
    case topLeft, topRight, bottomLeft, bottomRight
}

/// Draws an L-shaped accent at one corner of its bounding rect.
private struct CornerShape: Shape {
    let corner: Corner
    let length: CGFloat

    func path(in rect: CGRect) -> Path {
        var path = Path()
        switch corner {
        case .topLeft:
            path.move(to: CGPoint(x: rect.minX, y: rect.minY + length))
            path.addLine(to: CGPoint(x: rect.minX, y: rect.minY))
            path.addLine(to: CGPoint(x: rect.minX + length, y: rect.minY))
        case .topRight:
            path.move(to: CGPoint(x: rect.maxX - length, y: rect.minY))
            path.addLine(to: CGPoint(x: rect.maxX, y: rect.minY))
            path.addLine(to: CGPoint(x: rect.maxX, y: rect.minY + length))
        case .bottomLeft:
            path.move(to: CGPoint(x: rect.minX, y: rect.maxY - length))
            path.addLine(to: CGPoint(x: rect.minX, y: rect.maxY))
            path.addLine(to: CGPoint(x: rect.minX + length, y: rect.maxY))
        case .bottomRight:
            path.move(to: CGPoint(x: rect.maxX - length, y: rect.maxY))
            path.addLine(to: CGPoint(x: rect.maxX, y: rect.maxY))
            path.addLine(to: CGPoint(x: rect.maxX, y: rect.maxY - length))
        }
        return path
    }
}
