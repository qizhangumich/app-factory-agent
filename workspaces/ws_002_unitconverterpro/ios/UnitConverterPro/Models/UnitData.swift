import Foundation

/// A single convertible unit.
///
/// Most units are linear: `base = value * factor + offset`. Temperature units
/// override this with a closed-form conversion handled in `ConversionEngine`.
struct ConvUnit: Identifiable, Hashable {
    let id: String          // stable key, e.g. "length.meter"
    let name: String        // localization key suffix, resolved at display time
    let symbol: String      // short symbol, e.g. "m"
    let factor: Double      // multiply a value in this unit by `factor` to get the base unit
    let offset: Double      // additive offset (used only by temperature)

    init(id: String, name: String, symbol: String, factor: Double, offset: Double = 0) {
        self.id = id
        self.name = name
        self.symbol = symbol
        self.factor = factor
        self.offset = offset
    }
}

/// A group of mutually-convertible units.
struct UnitCategory: Identifiable, Hashable {
    let id: String          // stable key, e.g. "length"
    let name: String        // localization key suffix
    let systemImage: String // SF Symbol name
    let units: [ConvUnit]
    let isTemperature: Bool

    init(id: String, name: String, systemImage: String, units: [ConvUnit], isTemperature: Bool = false) {
        self.id = id
        self.name = name
        self.systemImage = systemImage
        self.units = units
        self.isTemperature = isTemperature
    }

    func unit(withID unitID: String) -> ConvUnit? {
        units.first { $0.id == unitID }
    }
}

/// Static catalog of every supported category and unit.
///
/// Linear factors express "how many base units equal one of this unit".
/// Base units: Length=meter, Weight=kilogram, Speed=m/s, Volume=liter,
/// Area=square meter, Data=bit, Time=second, Pressure=pascal, Energy=joule,
/// Power=watt, Angle=degree, Force=newton, Frequency=hertz,
/// FuelEconomy=km per liter, Cooking=milliliter.
/// All factors are NIST / SI reference values.
enum UnitData {

    static let categories: [UnitCategory] = [
        length, weight, temperature, speed, volume, area, data, time,
        pressure, energy, power, angle, force, frequency, fuelEconomy, cooking
    ]

    static func category(withID id: String) -> UnitCategory? {
        categories.first { $0.id == id }
    }

    // MARK: - Length (base: meter)
    static let length = UnitCategory(
        id: "length", name: "cat_length", systemImage: "ruler",
        units: [
            ConvUnit(id: "length.kilometer",    name: "u_kilometer",    symbol: "km",  factor: 1000),
            ConvUnit(id: "length.meter",        name: "u_meter",        symbol: "m",   factor: 1),
            ConvUnit(id: "length.centimeter",   name: "u_centimeter",   symbol: "cm",  factor: 0.01),
            ConvUnit(id: "length.millimeter",   name: "u_millimeter",   symbol: "mm",  factor: 0.001),
            ConvUnit(id: "length.micrometer",   name: "u_micrometer",   symbol: "µm",  factor: 1e-6),
            ConvUnit(id: "length.nanometer",    name: "u_nanometer",    symbol: "nm",  factor: 1e-9),
            ConvUnit(id: "length.mile",         name: "u_mile",         symbol: "mi",  factor: 1609.344),
            ConvUnit(id: "length.yard",         name: "u_yard",         symbol: "yd",  factor: 0.9144),
            ConvUnit(id: "length.foot",         name: "u_foot",         symbol: "ft",  factor: 0.3048),
            ConvUnit(id: "length.inch",         name: "u_inch",         symbol: "in",  factor: 0.0254),
            ConvUnit(id: "length.nauticalMile", name: "u_nautical_mile", symbol: "nmi", factor: 1852),
            ConvUnit(id: "length.lightYear",    name: "u_light_year",   symbol: "ly",  factor: 9.4607304725808e15)
        ])

    // MARK: - Weight (base: kilogram)
    static let weight = UnitCategory(
        id: "weight", name: "cat_weight", systemImage: "scalemass",
        units: [
            ConvUnit(id: "weight.metricTon",  name: "u_metric_ton",  symbol: "t",   factor: 1000),
            ConvUnit(id: "weight.kilogram",   name: "u_kilogram",    symbol: "kg",  factor: 1),
            ConvUnit(id: "weight.gram",       name: "u_gram",        symbol: "g",   factor: 0.001),
            ConvUnit(id: "weight.milligram",  name: "u_milligram",   symbol: "mg",  factor: 1e-6),
            ConvUnit(id: "weight.microgram",  name: "u_microgram",   symbol: "µg",  factor: 1e-9),
            ConvUnit(id: "weight.pound",      name: "u_pound",       symbol: "lb",  factor: 0.45359237),
            ConvUnit(id: "weight.ounce",      name: "u_ounce",       symbol: "oz",  factor: 0.028349523125),
            ConvUnit(id: "weight.stone",      name: "u_stone",       symbol: "st",  factor: 6.35029318),
            ConvUnit(id: "weight.shortTon",   name: "u_short_ton",   symbol: "ton", factor: 907.18474),
            ConvUnit(id: "weight.longTon",    name: "u_long_ton",    symbol: "LT",  factor: 1016.0469088),
            ConvUnit(id: "weight.carat",      name: "u_carat",       symbol: "ct",  factor: 0.0002)
        ])

    // MARK: - Temperature (special-cased; factor/offset unused for math)
    static let temperature = UnitCategory(
        id: "temperature", name: "cat_temperature", systemImage: "thermometer.medium",
        units: [
            ConvUnit(id: "temperature.celsius",    name: "u_celsius",    symbol: "°C", factor: 1),
            ConvUnit(id: "temperature.fahrenheit", name: "u_fahrenheit", symbol: "°F", factor: 1),
            ConvUnit(id: "temperature.kelvin",     name: "u_kelvin",     symbol: "K",  factor: 1)
        ], isTemperature: true)

    // MARK: - Speed (base: meter per second)
    static let speed = UnitCategory(
        id: "speed", name: "cat_speed", systemImage: "speedometer",
        units: [
            ConvUnit(id: "speed.mps",   name: "u_mps",   symbol: "m/s",  factor: 1),
            ConvUnit(id: "speed.kmh",   name: "u_kmh",   symbol: "km/h", factor: 0.277777777777778),
            ConvUnit(id: "speed.mph",   name: "u_mph",   symbol: "mph",  factor: 0.44704),
            ConvUnit(id: "speed.knot",  name: "u_knot",  symbol: "kn",   factor: 0.514444444444444),
            ConvUnit(id: "speed.fps",   name: "u_fps",   symbol: "ft/s", factor: 0.3048),
            ConvUnit(id: "speed.mach",  name: "u_mach",  symbol: "Mach", factor: 340.29)
        ])

    // MARK: - Volume (base: liter)
    static let volume = UnitCategory(
        id: "volume", name: "cat_volume", systemImage: "drop",
        units: [
            ConvUnit(id: "volume.literCubicMeter", name: "u_cubic_meter",  symbol: "m³",   factor: 1000),
            ConvUnit(id: "volume.liter",           name: "u_liter",        symbol: "L",    factor: 1),
            ConvUnit(id: "volume.milliliter",      name: "u_milliliter",   symbol: "mL",   factor: 0.001),
            ConvUnit(id: "volume.cubicCentimeter", name: "u_cubic_cm",     symbol: "cm³",  factor: 0.001),
            ConvUnit(id: "volume.usGallon",        name: "u_us_gallon",    symbol: "gal",  factor: 3.785411784),
            ConvUnit(id: "volume.usQuart",         name: "u_us_quart",     symbol: "qt",   factor: 0.946352946),
            ConvUnit(id: "volume.usPint",          name: "u_us_pint",      symbol: "pt",   factor: 0.473176473),
            ConvUnit(id: "volume.usCup",           name: "u_us_cup",       symbol: "cup",  factor: 0.2365882365),
            ConvUnit(id: "volume.usFluidOunce",    name: "u_us_fl_oz",     symbol: "fl oz", factor: 0.0295735295625),
            ConvUnit(id: "volume.impGallon",       name: "u_imp_gallon",   symbol: "gal UK", factor: 4.54609),
            ConvUnit(id: "volume.cubicInch",       name: "u_cubic_inch",   symbol: "in³",  factor: 0.016387064)
        ])

    // MARK: - Area (base: square meter)
    static let area = UnitCategory(
        id: "area", name: "cat_area", systemImage: "square.dashed",
        units: [
            ConvUnit(id: "area.squareKilometer",  name: "u_sq_kilometer",  symbol: "km²", factor: 1_000_000),
            ConvUnit(id: "area.hectare",          name: "u_hectare",       symbol: "ha",  factor: 10_000),
            ConvUnit(id: "area.squareMeter",      name: "u_sq_meter",      symbol: "m²",  factor: 1),
            ConvUnit(id: "area.squareCentimeter", name: "u_sq_centimeter", symbol: "cm²", factor: 0.0001),
            ConvUnit(id: "area.squareMile",       name: "u_sq_mile",       symbol: "mi²", factor: 2_589_988.110336),
            ConvUnit(id: "area.acre",             name: "u_acre",          symbol: "ac",  factor: 4046.8564224),
            ConvUnit(id: "area.squareYard",       name: "u_sq_yard",       symbol: "yd²", factor: 0.83612736),
            ConvUnit(id: "area.squareFoot",       name: "u_sq_foot",       symbol: "ft²", factor: 0.09290304),
            ConvUnit(id: "area.squareInch",       name: "u_sq_inch",       symbol: "in²", factor: 0.00064516)
        ])

    // MARK: - Data Storage (base: bit)
    static let data = UnitCategory(
        id: "data", name: "cat_data", systemImage: "externaldrive",
        units: [
            ConvUnit(id: "data.bit",      name: "u_bit",      symbol: "bit",  factor: 1),
            ConvUnit(id: "data.byte",     name: "u_byte",     symbol: "B",    factor: 8),
            ConvUnit(id: "data.kilobit",  name: "u_kilobit",  symbol: "Kbit", factor: 1000),
            ConvUnit(id: "data.kilobyte", name: "u_kilobyte", symbol: "KB",   factor: 8000),
            ConvUnit(id: "data.megabit",  name: "u_megabit",  symbol: "Mbit", factor: 1e6),
            ConvUnit(id: "data.megabyte", name: "u_megabyte", symbol: "MB",   factor: 8e6),
            ConvUnit(id: "data.gigabit",  name: "u_gigabit",  symbol: "Gbit", factor: 1e9),
            ConvUnit(id: "data.gigabyte", name: "u_gigabyte", symbol: "GB",   factor: 8e9),
            ConvUnit(id: "data.terabyte", name: "u_terabyte", symbol: "TB",   factor: 8e12),
            ConvUnit(id: "data.petabyte", name: "u_petabyte", symbol: "PB",   factor: 8e15)
        ])

    // MARK: - Time (base: second)
    static let time = UnitCategory(
        id: "time", name: "cat_time", systemImage: "clock",
        units: [
            ConvUnit(id: "time.nanosecond",  name: "u_nanosecond",  symbol: "ns",  factor: 1e-9),
            ConvUnit(id: "time.microsecond", name: "u_microsecond", symbol: "µs",  factor: 1e-6),
            ConvUnit(id: "time.millisecond", name: "u_millisecond", symbol: "ms",  factor: 0.001),
            ConvUnit(id: "time.second",      name: "u_second",      symbol: "s",   factor: 1),
            ConvUnit(id: "time.minute",      name: "u_minute",      symbol: "min", factor: 60),
            ConvUnit(id: "time.hour",        name: "u_hour",        symbol: "h",   factor: 3600),
            ConvUnit(id: "time.day",         name: "u_day",         symbol: "d",   factor: 86_400),
            ConvUnit(id: "time.week",        name: "u_week",        symbol: "wk",  factor: 604_800),
            ConvUnit(id: "time.month",       name: "u_month",       symbol: "mo",  factor: 2_629_746),
            ConvUnit(id: "time.year",        name: "u_year",        symbol: "yr",  factor: 31_556_952)
        ])

    // MARK: - Pressure (base: pascal)
    static let pressure = UnitCategory(
        id: "pressure", name: "cat_pressure", systemImage: "gauge.with.dots.needle.bottom.50percent",
        units: [
            ConvUnit(id: "pressure.pascal",     name: "u_pascal",     symbol: "Pa",   factor: 1),
            ConvUnit(id: "pressure.kilopascal", name: "u_kilopascal", symbol: "kPa",  factor: 1000),
            ConvUnit(id: "pressure.bar",        name: "u_bar",        symbol: "bar",  factor: 100_000),
            ConvUnit(id: "pressure.psi",        name: "u_psi",        symbol: "psi",  factor: 6894.757293168),
            ConvUnit(id: "pressure.atmosphere", name: "u_atmosphere", symbol: "atm",  factor: 101_325),
            ConvUnit(id: "pressure.torr",       name: "u_torr",       symbol: "Torr", factor: 133.322368421),
            ConvUnit(id: "pressure.mmHg",       name: "u_mmhg",       symbol: "mmHg", factor: 133.322387415)
        ])

    // MARK: - Energy (base: joule)
    static let energy = UnitCategory(
        id: "energy", name: "cat_energy", systemImage: "bolt",
        units: [
            ConvUnit(id: "energy.joule",        name: "u_joule",        symbol: "J",    factor: 1),
            ConvUnit(id: "energy.kilojoule",    name: "u_kilojoule",    symbol: "kJ",   factor: 1000),
            ConvUnit(id: "energy.calorie",      name: "u_calorie",      symbol: "cal",  factor: 4.184),
            ConvUnit(id: "energy.kilocalorie",  name: "u_kilocalorie",  symbol: "kcal", factor: 4184),
            ConvUnit(id: "energy.wattHour",     name: "u_watt_hour",    symbol: "Wh",   factor: 3600),
            ConvUnit(id: "energy.kilowattHour", name: "u_kilowatt_hour", symbol: "kWh", factor: 3_600_000),
            ConvUnit(id: "energy.electronVolt", name: "u_electron_volt", symbol: "eV",  factor: 1.602176634e-19),
            ConvUnit(id: "energy.btu",          name: "u_btu",          symbol: "BTU",  factor: 1055.05585262),
            ConvUnit(id: "energy.footPound",    name: "u_foot_pound",   symbol: "ft·lb", factor: 1.3558179483314)
        ])

    // MARK: - Power (base: watt)
    static let power = UnitCategory(
        id: "power", name: "cat_power", systemImage: "powerplug",
        units: [
            ConvUnit(id: "power.watt",          name: "u_watt",           symbol: "W",   factor: 1),
            ConvUnit(id: "power.kilowatt",      name: "u_kilowatt",       symbol: "kW",  factor: 1000),
            ConvUnit(id: "power.megawatt",      name: "u_megawatt",       symbol: "MW",  factor: 1e6),
            ConvUnit(id: "power.horsepower",    name: "u_horsepower",     symbol: "hp",  factor: 745.69987158227),
            ConvUnit(id: "power.metricHp",      name: "u_metric_hp",      symbol: "PS",  factor: 735.49875),
            ConvUnit(id: "power.btuPerHour",    name: "u_btu_per_hour",   symbol: "BTU/h", factor: 0.29307107),
            ConvUnit(id: "power.footPoundPerSec", name: "u_ftlb_per_sec", symbol: "ft·lb/s", factor: 1.3558179483314)
        ])

    // MARK: - Angle (base: degree)
    static let angle = UnitCategory(
        id: "angle", name: "cat_angle", systemImage: "angle",
        units: [
            ConvUnit(id: "angle.degree",     name: "u_degree",     symbol: "°",    factor: 1),
            ConvUnit(id: "angle.radian",     name: "u_radian",     symbol: "rad",  factor: 57.2957795130823),
            ConvUnit(id: "angle.gradian",    name: "u_gradian",    symbol: "grad", factor: 0.9),
            ConvUnit(id: "angle.arcminute",  name: "u_arcminute",  symbol: "'",    factor: 0.0166666666666667),
            ConvUnit(id: "angle.arcsecond",  name: "u_arcsecond",  symbol: "\"",   factor: 0.000277777777777778),
            ConvUnit(id: "angle.revolution", name: "u_revolution", symbol: "rev",  factor: 360)
        ])

    // MARK: - Force (base: newton)
    static let force = UnitCategory(
        id: "force", name: "cat_force", systemImage: "arrow.down.to.line",
        units: [
            ConvUnit(id: "force.newton",       name: "u_newton",       symbol: "N",   factor: 1),
            ConvUnit(id: "force.kilonewton",   name: "u_kilonewton",   symbol: "kN",  factor: 1000),
            ConvUnit(id: "force.dyne",         name: "u_dyne",         symbol: "dyn", factor: 1e-5),
            ConvUnit(id: "force.poundForce",   name: "u_pound_force",  symbol: "lbf", factor: 4.4482216152605),
            ConvUnit(id: "force.kilogramForce", name: "u_kilogram_force", symbol: "kgf", factor: 9.80665),
            ConvUnit(id: "force.ounceForce",   name: "u_ounce_force",  symbol: "ozf", factor: 0.27801385095378)
        ])

    // MARK: - Frequency (base: hertz)
    static let frequency = UnitCategory(
        id: "frequency", name: "cat_frequency", systemImage: "waveform",
        units: [
            ConvUnit(id: "frequency.hertz",     name: "u_hertz",     symbol: "Hz",  factor: 1),
            ConvUnit(id: "frequency.kilohertz", name: "u_kilohertz", symbol: "kHz", factor: 1000),
            ConvUnit(id: "frequency.megahertz", name: "u_megahertz", symbol: "MHz", factor: 1e6),
            ConvUnit(id: "frequency.gigahertz", name: "u_gigahertz", symbol: "GHz", factor: 1e9),
            ConvUnit(id: "frequency.rpm",       name: "u_rpm",       symbol: "rpm", factor: 0.0166666666666667)
        ])

    // MARK: - Fuel Economy (base: kilometer per liter)
    // Note: mpg <-> km/L is linear; L/100km is handled via reciprocal in the engine.
    static let fuelEconomy = UnitCategory(
        id: "fuelEconomy", name: "cat_fuel", systemImage: "fuelpump",
        units: [
            ConvUnit(id: "fuelEconomy.kmPerLiter", name: "u_km_per_liter", symbol: "km/L", factor: 1),
            ConvUnit(id: "fuelEconomy.mpgUS",      name: "u_mpg_us",       symbol: "mpg",  factor: 0.425143707),
            ConvUnit(id: "fuelEconomy.mpgUK",      name: "u_mpg_uk",       symbol: "mpg UK", factor: 0.354006042),
            ConvUnit(id: "fuelEconomy.milesPerLiter", name: "u_miles_per_liter", symbol: "mi/L", factor: 1.609344)
        ])

    // MARK: - Cooking (base: milliliter)
    static let cooking = UnitCategory(
        id: "cooking", name: "cat_cooking", systemImage: "fork.knife",
        units: [
            ConvUnit(id: "cooking.milliliter",  name: "u_milliliter",   symbol: "mL",   factor: 1),
            ConvUnit(id: "cooking.liter",       name: "u_liter",        symbol: "L",    factor: 1000),
            ConvUnit(id: "cooking.teaspoon",    name: "u_teaspoon",     symbol: "tsp",  factor: 4.92892159375),
            ConvUnit(id: "cooking.tablespoon",  name: "u_tablespoon",   symbol: "tbsp", factor: 14.78676478125),
            ConvUnit(id: "cooking.cupUS",       name: "u_cup_us",       symbol: "cup",  factor: 236.5882365),
            ConvUnit(id: "cooking.cupMetric",   name: "u_cup_metric",   symbol: "cup M", factor: 250),
            ConvUnit(id: "cooking.fluidOunce",  name: "u_us_fl_oz",     symbol: "fl oz", factor: 29.5735295625),
            ConvUnit(id: "cooking.pintUS",      name: "u_us_pint",      symbol: "pt",   factor: 473.176473),
            ConvUnit(id: "cooking.quartUS",     name: "u_us_quart",     symbol: "qt",   factor: 946.352946),
            ConvUnit(id: "cooking.gallonUS",    name: "u_us_gallon",    symbol: "gal",  factor: 3785.411784)
        ])
}
