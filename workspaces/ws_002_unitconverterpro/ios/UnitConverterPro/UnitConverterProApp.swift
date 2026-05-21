import SwiftUI

@main
struct UnitConverterProApp: App {
    @StateObject private var store = AppStore()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(store)
                .tint(.indigo)
        }
    }
}

/// Root tab container: Convert (category list) and History.
struct RootView: View {
    var body: some View {
        TabView {
            NavigationStack {
                CategoryListView()
            }
            .tabItem {
                Label(L.string("tab_convert"), systemImage: "arrow.left.arrow.right")
            }

            NavigationStack {
                HistoryView()
            }
            .tabItem {
                Label(L.string("tab_history"), systemImage: "clock.arrow.circlepath")
            }
        }
    }
}
