import SwiftUI

/// Shown when microphone access has been denied. Guides the user to Settings.
struct PermissionDeniedView: View {
    var body: some View {
        VStack(spacing: 18) {
            Image(systemName: "mic.slash.circle")
                .font(.system(size: 64))
                .foregroundColor(.secondary)

            Text("permission.deniedTitle")
                .font(.title3)
                .fontWeight(.bold)
                .multilineTextAlignment(.center)

            Text("permission.deniedBody")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)

            Button {
                if let url = URL(string: UIApplication.openSettingsURLString) {
                    UIApplication.shared.open(url)
                }
            } label: {
                Text("permission.openSettings")
                    .fontWeight(.semibold)
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
        }
        .padding(32)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(.systemBackground))
    }
}

#Preview {
    PermissionDeniedView()
}
