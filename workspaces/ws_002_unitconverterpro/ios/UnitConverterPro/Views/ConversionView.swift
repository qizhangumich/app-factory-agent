import SwiftUI

/// Screen 2: the two-field converter with live conversion, swap, favorite,
/// copy, and a related-conversions list.
struct ConversionView: View {
    @EnvironmentObject private var store: AppStore

    let category: UnitCategory

    @State private var fromUnit: ConvUnit
    @State private var toUnit: ConvUnit
    @State private var inputText: String
    @State private var showCopied = false
    @FocusState private var inputFocused: Bool

    /// `historyDebounce` collapses a burst of keystrokes into a single record.
    @State private var historyWorkItem: DispatchWorkItem?

    init(category: UnitCategory,
         initialFromID: String? = nil,
         initialToID: String? = nil,
         initialValue: String = "1") {
        self.category = category
        let from = category.unit(withID: initialFromID ?? "")
            ?? category.units[0]
        let to = category.unit(withID: initialToID ?? "")
            ?? (category.units.count > 1 ? category.units[1] : category.units[0])
        _fromUnit = State(initialValue: from)
        _toUnit = State(initialValue: to)
        _inputText = State(initialValue: initialValue)
    }

    var body: some View {
        ScrollView {
            VStack(spacing: 18) {
                converterCard
                actionRow
                relatedSection
            }
            .padding()
        }
        .background(Color(.systemGroupedBackground))
        .navigationTitle(category.localizedName)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button {
                    store.toggleFavorite(categoryID: category.id,
                                         fromUnitID: fromUnit.id,
                                         toUnitID: toUnit.id)
                } label: {
                    Image(systemName: isFavorite ? "star.fill" : "star")
                        .foregroundStyle(isFavorite ? .yellow : .secondary)
                }
                .accessibilityLabel(Text(isFavorite
                    ? L.string("a11y_unfavorite")
                    : L.string("a11y_favorite")))
            }
        }
        .overlay(alignment: .bottom) {
            if showCopied {
                Text(L.string("toast_copied"))
                    .font(.subheadline.weight(.semibold))
                    .padding(.horizontal, 16).padding(.vertical, 10)
                    .background(.thinMaterial, in: Capsule())
                    .padding(.bottom, 24)
                    .transition(.move(edge: .bottom).combined(with: .opacity))
            }
        }
    }

    // MARK: - Converter card

    private var converterCard: some View {
        VStack(spacing: 0) {
            // From
            UnitFieldRow(
                role: L.string("label_from"),
                category: category,
                selectedUnit: $fromUnit,
                value: Binding(get: { inputText }, set: { newValue in
                    inputText = sanitize(newValue)
                    scheduleHistory()
                }),
                isEditable: true,
                isFocused: $inputFocused
            )

            // Swap button
            ZStack {
                Divider()
                Button {
                    swap()
                } label: {
                    Image(systemName: "arrow.up.arrow.down.circle.fill")
                        .font(.system(size: 36))
                        .foregroundStyle(.white, .orange)
                        .background(Circle().fill(Color(.secondarySystemGroupedBackground)))
                }
                .accessibilityLabel(Text(L.string("a11y_swap")))
            }
            .frame(height: 24)

            // To
            UnitFieldRow(
                role: L.string("label_to"),
                category: category,
                selectedUnit: $toUnit,
                value: .constant(resultString),
                isEditable: false,
                isFocused: $inputFocused
            )
        }
        .padding(16)
        .background(Color(.secondarySystemGroupedBackground))
        .clipShape(RoundedRectangle(cornerRadius: 20))
    }

    // MARK: - Action row

    private var actionRow: some View {
        HStack(spacing: 12) {
            Button {
                copyResult()
            } label: {
                Label(L.string("action_copy"), systemImage: "doc.on.doc")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .tint(.indigo)
            .disabled(parsedInput == nil)

            Button {
                store.toggleFavorite(categoryID: category.id,
                                     fromUnitID: fromUnit.id,
                                     toUnitID: toUnit.id)
            } label: {
                Label(isFavorite ? L.string("action_unfavorite")
                                 : L.string("action_favorite"),
                      systemImage: isFavorite ? "star.fill" : "star")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.bordered)
            .tint(.yellow)
        }
    }

    // MARK: - Related conversions

    private var relatedSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L.string("section_related"))
                .font(.headline)
                .foregroundStyle(.secondary)
                .frame(maxWidth: .infinity, alignment: .leading)

            ForEach(relatedUnits, id: \.id) { unit in
                HStack {
                    Text(unit.displayLabel)
                        .foregroundStyle(.primary)
                    Spacer()
                    Text(relatedValue(for: unit))
                        .font(.body.monospacedDigit())
                        .foregroundStyle(.secondary)
                }
                .padding(.vertical, 10)
                .padding(.horizontal, 14)
                .background(Color(.secondarySystemGroupedBackground))
                .clipShape(RoundedRectangle(cornerRadius: 12))
                .contentShape(Rectangle())
                .onTapGesture { toUnit = unit }
            }
        }
    }

    // MARK: - Derived values

    private var parsedInput: Double? {
        ConversionEngine.parse(inputText)
    }

    private var resultValue: Double? {
        guard let input = parsedInput else { return nil }
        return ConversionEngine.convert(input,
                                        from: fromUnit,
                                        to: toUnit,
                                        category: category)
    }

    private var resultString: String {
        guard let r = resultValue else { return "" }
        return ConversionEngine.format(r)
    }

    private var isFavorite: Bool {
        store.isFavorite(categoryID: category.id,
                         fromUnitID: fromUnit.id,
                         toUnitID: toUnit.id)
    }

    /// Up to five other units in the category, excluding the current target.
    private var relatedUnits: [ConvUnit] {
        category.units
            .filter { $0.id != toUnit.id && $0.id != fromUnit.id }
            .prefix(5)
            .map { $0 }
    }

    private func relatedValue(for unit: ConvUnit) -> String {
        guard let input = parsedInput,
              let r = ConversionEngine.convert(input,
                                               from: fromUnit,
                                               to: unit,
                                               category: category) else {
            return "—"
        }
        return ConversionEngine.format(r)
    }

    // MARK: - Actions

    private func swap() {
        let oldFrom = fromUnit
        fromUnit = toUnit
        toUnit = oldFrom
        // Carry the displayed result into the input so the swap is meaningful.
        if let r = resultValue {
            inputText = ConversionEngine.format(r)
                .replacingOccurrences(of: ",", with: "")
        }
        scheduleHistory()
    }

    private func copyResult() {
        guard let r = resultValue else { return }
        UIPasteboard.general.string = ConversionEngine.format(r)
        withAnimation { showCopied = true }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.6) {
            withAnimation { showCopied = false }
        }
    }

    /// Records the current conversion to history after a short idle delay.
    private func scheduleHistory() {
        historyWorkItem?.cancel()
        let work = DispatchWorkItem {
            guard let input = parsedInput, let r = resultValue else { return }
            store.addHistory(categoryID: category.id,
                             fromUnitID: fromUnit.id,
                             toUnitID: toUnit.id,
                             inputValue: input,
                             resultValue: r)
        }
        historyWorkItem = work
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0, execute: work)
    }

    /// Keeps the input field to characters that can form a number.
    private func sanitize(_ raw: String) -> String {
        let allowed = Set("0123456789.,-eE ")
        return String(raw.filter { allowed.contains($0) })
    }
}

/// One labeled row of the converter: a value field plus a unit picker.
struct UnitFieldRow: View {
    let role: String
    let category: UnitCategory
    @Binding var selectedUnit: ConvUnit
    @Binding var value: String
    let isEditable: Bool
    var isFocused: FocusState<Bool>.Binding

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(role)
                .font(.caption.weight(.semibold))
                .foregroundStyle(.secondary)

            HStack(spacing: 12) {
                if isEditable {
                    TextField("0", text: $value)
                        .keyboardType(.numbersAndPunctuation)
                        .font(.system(.title2, design: .rounded).weight(.semibold))
                        .focused(isFocused)
                        .accessibilityLabel(Text(role))
                } else {
                    Text(value.isEmpty ? "—" : value)
                        .font(.system(.title2, design: .rounded).weight(.semibold))
                        .foregroundStyle(.primary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .accessibilityLabel(Text("\(role): \(value)"))
                }

                Menu {
                    ForEach(category.units) { unit in
                        Button {
                            selectedUnit = unit
                        } label: {
                            if unit.id == selectedUnit.id {
                                Label(unit.displayLabel, systemImage: "checkmark")
                            } else {
                                Text(unit.displayLabel)
                            }
                        }
                    }
                } label: {
                    HStack(spacing: 4) {
                        Text(selectedUnit.symbol)
                            .font(.headline)
                        Image(systemName: "chevron.up.chevron.down")
                            .font(.caption2)
                    }
                    .padding(.horizontal, 12).padding(.vertical, 8)
                    .background(Color(.tertiarySystemGroupedBackground))
                    .clipShape(Capsule())
                }
                .accessibilityLabel(Text(String(format: L.string("a11y_unit_picker"),
                                                selectedUnit.localizedName)))
            }
        }
        .padding(.vertical, 10)
    }
}
