import SwiftUI

/// Screen 1: searchable category grid with a pinned favorites row.
struct CategoryListView: View {
    @EnvironmentObject private var store: AppStore
    @State private var searchText = ""

    private let columns = [GridItem(.adaptive(minimum: 150), spacing: 14)]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                if !store.favorites.isEmpty && searchText.isEmpty {
                    favoritesSection
                }

                if filteredCategories.isEmpty && !unitMatches.isEmpty {
                    unitSearchResults
                } else {
                    categoryGrid
                }
            }
            .padding(.horizontal)
            .padding(.top, 8)
        }
        .background(Color(.systemGroupedBackground))
        .navigationTitle(L.string("app_name"))
        .searchable(text: $searchText,
                    prompt: Text(L.string("search_prompt")))
    }

    // MARK: - Favorites

    private var favoritesSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L.string("section_favorites"))
                .font(.headline)
                .foregroundStyle(.secondary)

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    ForEach(store.favorites) { fav in
                        favoriteCard(for: fav)
                    }
                }
                .padding(.vertical, 2)
            }
        }
    }

    @ViewBuilder
    private func favoriteCard(for fav: FavoritePair) -> some View {
        if let category = UnitData.category(withID: fav.categoryID),
           let from = category.unit(withID: fav.fromUnitID),
           let to = category.unit(withID: fav.toUnitID) {
            NavigationLink {
                ConversionView(category: category,
                               initialFromID: from.id,
                               initialToID: to.id)
            } label: {
                VStack(alignment: .leading, spacing: 6) {
                    Image(systemName: category.systemImage)
                        .font(.title3)
                        .foregroundStyle(.indigo)
                    Text("\(from.symbol) → \(to.symbol)")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(.primary)
                    Text(category.localizedName)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                .frame(width: 130, alignment: .leading)
                .padding(12)
                .background(Color(.secondarySystemGroupedBackground))
                .clipShape(RoundedRectangle(cornerRadius: 14))
            }
            .buttonStyle(.plain)
            .accessibilityLabel(Text(String(format: L.string("a11y_favorite_pair"),
                                            from.localizedName,
                                            to.localizedName,
                                            category.localizedName)))
        }
    }

    // MARK: - Category grid

    private var categoryGrid: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L.string("section_categories"))
                .font(.headline)
                .foregroundStyle(.secondary)

            LazyVGrid(columns: columns, spacing: 14) {
                ForEach(filteredCategories) { category in
                    NavigationLink {
                        ConversionView(category: category)
                    } label: {
                        CategoryCard(category: category)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }

    // MARK: - Unit search results

    private var unitSearchResults: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L.string("section_unit_results"))
                .font(.headline)
                .foregroundStyle(.secondary)

            ForEach(unitMatches, id: \.unit.id) { match in
                NavigationLink {
                    ConversionView(category: match.category,
                                   initialFromID: match.unit.id)
                } label: {
                    HStack {
                        Image(systemName: match.category.systemImage)
                            .foregroundStyle(.indigo)
                            .frame(width: 28)
                        VStack(alignment: .leading) {
                            Text(match.unit.displayLabel)
                                .foregroundStyle(.primary)
                            Text(match.category.localizedName)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                        Spacer()
                        Image(systemName: "chevron.right")
                            .font(.caption)
                            .foregroundStyle(.tertiary)
                    }
                    .padding(12)
                    .background(Color(.secondarySystemGroupedBackground))
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .buttonStyle(.plain)
            }
        }
    }

    // MARK: - Filtering

    private var filteredCategories: [UnitCategory] {
        guard !searchText.isEmpty else { return UnitData.categories }
        let q = searchText.lowercased()
        return UnitData.categories.filter {
            $0.localizedName.lowercased().contains(q)
        }
    }

    /// Units whose name or symbol matches the query, used when no category name does.
    private var unitMatches: [(category: UnitCategory, unit: ConvUnit)] {
        guard !searchText.isEmpty else { return [] }
        let q = searchText.lowercased()
        var results: [(UnitCategory, ConvUnit)] = []
        for category in UnitData.categories {
            for unit in category.units {
                if unit.localizedName.lowercased().contains(q) ||
                    unit.symbol.lowercased().contains(q) {
                    results.append((category, unit))
                }
            }
        }
        return results
    }
}

/// One tile in the category grid. Shows the category icon, name, and the two
/// representative units as a subtitle.
struct CategoryCard: View {
    let category: UnitCategory

    private var subtitle: String {
        category.units.prefix(2).map { $0.symbol }.joined(separator: " · ")
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Image(systemName: category.systemImage)
                .font(.title)
                .foregroundStyle(.indigo)
                .frame(height: 32)
            Text(category.localizedName)
                .font(.headline)
                .foregroundStyle(.primary)
            Text(subtitle)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, minHeight: 120, alignment: .leading)
        .padding(14)
        .background(Color(.secondarySystemGroupedBackground))
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .accessibilityElement(children: .combine)
        .accessibilityLabel(Text(category.localizedName))
        .accessibilityHint(Text(L.string("a11y_open_category")))
    }
}
