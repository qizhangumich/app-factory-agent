package com.appfactory.unitconverterpro.model

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AcUnit
import androidx.compose.material.icons.filled.Bolt
import androidx.compose.material.icons.filled.CropSquare
import androidx.compose.material.icons.filled.GraphicEq
import androidx.compose.material.icons.filled.Hardware
import androidx.compose.material.icons.filled.LocalGasStation
import androidx.compose.material.icons.filled.Power
import androidx.compose.material.icons.filled.Restaurant
import androidx.compose.material.icons.filled.Schedule
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material.icons.filled.SquareFoot
import androidx.compose.material.icons.filled.Storage
import androidx.compose.material.icons.filled.Straighten
import androidx.compose.material.icons.filled.Thermostat
import androidx.compose.material.icons.filled.Timeline
import androidx.compose.material.icons.filled.WaterDrop
import androidx.compose.ui.graphics.vector.ImageVector

/**
 * A single convertible unit. Linear units use base = value * factor.
 * Temperature is special-cased in [ConversionEngine].
 *
 * @property id stable key, e.g. "length.meter"
 * @property nameRes Android string resource id for the localized unit name
 * @property symbol short symbol, e.g. "m"
 * @property factor multiply a value in this unit by factor to get the base unit
 */
data class ConvUnit(
    val id: String,
    val nameRes: Int,
    val symbol: String,
    val factor: Double
)

/** A group of mutually-convertible units. */
data class UnitCategory(
    val id: String,
    val nameRes: Int,
    val icon: ImageVector,
    val units: List<ConvUnit>,
    val isTemperature: Boolean = false
) {
    fun unit(unitId: String): ConvUnit? = units.firstOrNull { it.id == unitId }
}

/**
 * Static catalog of every supported category and unit.
 *
 * Base units: Length=meter, Weight=kilogram, Speed=m/s, Volume=liter,
 * Area=square meter, Data=bit, Time=second, Pressure=pascal, Energy=joule,
 * Power=watt, Angle=degree, Force=newton, Frequency=hertz,
 * FuelEconomy=km per liter, Cooking=milliliter. All NIST / SI reference values.
 */
object UnitData {

    // String resource ids are resolved lazily via R; declared here as a holder
    // so the catalog stays a pure data structure. The actual ints come from R.
    // We reference them through [Res] to keep this file independent of R import
    // ordering during incremental builds.

    val categories: List<UnitCategory> by lazy {
        listOf(
            length, weight, temperature, speed, volume, area, data, time,
            pressure, energy, power, angle, force, frequency, fuelEconomy, cooking
        )
    }

    fun category(id: String): UnitCategory? = categories.firstOrNull { it.id == id }

    // Length (base: meter)
    private val length = UnitCategory(
        "length", Res.cat_length, Icons.Filled.Straighten,
        listOf(
            ConvUnit("length.kilometer", Res.u_kilometer, "km", 1000.0),
            ConvUnit("length.meter", Res.u_meter, "m", 1.0),
            ConvUnit("length.centimeter", Res.u_centimeter, "cm", 0.01),
            ConvUnit("length.millimeter", Res.u_millimeter, "mm", 0.001),
            ConvUnit("length.micrometer", Res.u_micrometer, "µm", 1e-6),
            ConvUnit("length.nanometer", Res.u_nanometer, "nm", 1e-9),
            ConvUnit("length.mile", Res.u_mile, "mi", 1609.344),
            ConvUnit("length.yard", Res.u_yard, "yd", 0.9144),
            ConvUnit("length.foot", Res.u_foot, "ft", 0.3048),
            ConvUnit("length.inch", Res.u_inch, "in", 0.0254),
            ConvUnit("length.nauticalMile", Res.u_nautical_mile, "nmi", 1852.0),
            ConvUnit("length.lightYear", Res.u_light_year, "ly", 9.4607304725808e15)
        )
    )

    // Weight (base: kilogram)
    private val weight = UnitCategory(
        "weight", Res.cat_weight, Icons.Filled.Hardware,
        listOf(
            ConvUnit("weight.metricTon", Res.u_metric_ton, "t", 1000.0),
            ConvUnit("weight.kilogram", Res.u_kilogram, "kg", 1.0),
            ConvUnit("weight.gram", Res.u_gram, "g", 0.001),
            ConvUnit("weight.milligram", Res.u_milligram, "mg", 1e-6),
            ConvUnit("weight.microgram", Res.u_microgram, "µg", 1e-9),
            ConvUnit("weight.pound", Res.u_pound, "lb", 0.45359237),
            ConvUnit("weight.ounce", Res.u_ounce, "oz", 0.028349523125),
            ConvUnit("weight.stone", Res.u_stone, "st", 6.35029318),
            ConvUnit("weight.shortTon", Res.u_short_ton, "ton", 907.18474),
            ConvUnit("weight.longTon", Res.u_long_ton, "LT", 1016.0469088),
            ConvUnit("weight.carat", Res.u_carat, "ct", 0.0002)
        )
    )

    // Temperature (factor unused; special-cased)
    private val temperature = UnitCategory(
        "temperature", Res.cat_temperature, Icons.Filled.Thermostat,
        listOf(
            ConvUnit("temperature.celsius", Res.u_celsius, "°C", 1.0),
            ConvUnit("temperature.fahrenheit", Res.u_fahrenheit, "°F", 1.0),
            ConvUnit("temperature.kelvin", Res.u_kelvin, "K", 1.0)
        ),
        isTemperature = true
    )

    // Speed (base: meter per second)
    private val speed = UnitCategory(
        "speed", Res.cat_speed, Icons.Filled.Speed,
        listOf(
            ConvUnit("speed.mps", Res.u_mps, "m/s", 1.0),
            ConvUnit("speed.kmh", Res.u_kmh, "km/h", 0.277777777777778),
            ConvUnit("speed.mph", Res.u_mph, "mph", 0.44704),
            ConvUnit("speed.knot", Res.u_knot, "kn", 0.514444444444444),
            ConvUnit("speed.fps", Res.u_fps, "ft/s", 0.3048),
            ConvUnit("speed.mach", Res.u_mach, "Mach", 340.29)
        )
    )

    // Volume (base: liter)
    private val volume = UnitCategory(
        "volume", Res.cat_volume, Icons.Filled.WaterDrop,
        listOf(
            ConvUnit("volume.cubicMeter", Res.u_cubic_meter, "m³", 1000.0),
            ConvUnit("volume.liter", Res.u_liter, "L", 1.0),
            ConvUnit("volume.milliliter", Res.u_milliliter, "mL", 0.001),
            ConvUnit("volume.cubicCentimeter", Res.u_cubic_cm, "cm³", 0.001),
            ConvUnit("volume.usGallon", Res.u_us_gallon, "gal", 3.785411784),
            ConvUnit("volume.usQuart", Res.u_us_quart, "qt", 0.946352946),
            ConvUnit("volume.usPint", Res.u_us_pint, "pt", 0.473176473),
            ConvUnit("volume.usCup", Res.u_us_cup, "cup", 0.2365882365),
            ConvUnit("volume.usFluidOunce", Res.u_us_fl_oz, "fl oz", 0.0295735295625),
            ConvUnit("volume.impGallon", Res.u_imp_gallon, "gal UK", 4.54609),
            ConvUnit("volume.cubicInch", Res.u_cubic_inch, "in³", 0.016387064)
        )
    )

    // Area (base: square meter)
    private val area = UnitCategory(
        "area", Res.cat_area, Icons.Filled.SquareFoot,
        listOf(
            ConvUnit("area.squareKilometer", Res.u_sq_kilometer, "km²", 1_000_000.0),
            ConvUnit("area.hectare", Res.u_hectare, "ha", 10_000.0),
            ConvUnit("area.squareMeter", Res.u_sq_meter, "m²", 1.0),
            ConvUnit("area.squareCentimeter", Res.u_sq_centimeter, "cm²", 0.0001),
            ConvUnit("area.squareMile", Res.u_sq_mile, "mi²", 2_589_988.110336),
            ConvUnit("area.acre", Res.u_acre, "ac", 4046.8564224),
            ConvUnit("area.squareYard", Res.u_sq_yard, "yd²", 0.83612736),
            ConvUnit("area.squareFoot", Res.u_sq_foot, "ft²", 0.09290304),
            ConvUnit("area.squareInch", Res.u_sq_inch, "in²", 0.00064516)
        )
    )

    // Data Storage (base: bit)
    private val data = UnitCategory(
        "data", Res.cat_data, Icons.Filled.Storage,
        listOf(
            ConvUnit("data.bit", Res.u_bit, "bit", 1.0),
            ConvUnit("data.byte", Res.u_byte, "B", 8.0),
            ConvUnit("data.kilobit", Res.u_kilobit, "Kbit", 1000.0),
            ConvUnit("data.kilobyte", Res.u_kilobyte, "KB", 8000.0),
            ConvUnit("data.megabit", Res.u_megabit, "Mbit", 1e6),
            ConvUnit("data.megabyte", Res.u_megabyte, "MB", 8e6),
            ConvUnit("data.gigabit", Res.u_gigabit, "Gbit", 1e9),
            ConvUnit("data.gigabyte", Res.u_gigabyte, "GB", 8e9),
            ConvUnit("data.terabyte", Res.u_terabyte, "TB", 8e12),
            ConvUnit("data.petabyte", Res.u_petabyte, "PB", 8e15)
        )
    )

    // Time (base: second)
    private val time = UnitCategory(
        "time", Res.cat_time, Icons.Filled.Schedule,
        listOf(
            ConvUnit("time.nanosecond", Res.u_nanosecond, "ns", 1e-9),
            ConvUnit("time.microsecond", Res.u_microsecond, "µs", 1e-6),
            ConvUnit("time.millisecond", Res.u_millisecond, "ms", 0.001),
            ConvUnit("time.second", Res.u_second, "s", 1.0),
            ConvUnit("time.minute", Res.u_minute, "min", 60.0),
            ConvUnit("time.hour", Res.u_hour, "h", 3600.0),
            ConvUnit("time.day", Res.u_day, "d", 86_400.0),
            ConvUnit("time.week", Res.u_week, "wk", 604_800.0),
            ConvUnit("time.month", Res.u_month, "mo", 2_629_746.0),
            ConvUnit("time.year", Res.u_year, "yr", 31_556_952.0)
        )
    )

    // Pressure (base: pascal)
    private val pressure = UnitCategory(
        "pressure", Res.cat_pressure, Icons.Filled.GraphicEq,
        listOf(
            ConvUnit("pressure.pascal", Res.u_pascal, "Pa", 1.0),
            ConvUnit("pressure.kilopascal", Res.u_kilopascal, "kPa", 1000.0),
            ConvUnit("pressure.bar", Res.u_bar, "bar", 100_000.0),
            ConvUnit("pressure.psi", Res.u_psi, "psi", 6894.757293168),
            ConvUnit("pressure.atmosphere", Res.u_atmosphere, "atm", 101_325.0),
            ConvUnit("pressure.torr", Res.u_torr, "Torr", 133.322368421),
            ConvUnit("pressure.mmHg", Res.u_mmhg, "mmHg", 133.322387415)
        )
    )

    // Energy (base: joule)
    private val energy = UnitCategory(
        "energy", Res.cat_energy, Icons.Filled.Bolt,
        listOf(
            ConvUnit("energy.joule", Res.u_joule, "J", 1.0),
            ConvUnit("energy.kilojoule", Res.u_kilojoule, "kJ", 1000.0),
            ConvUnit("energy.calorie", Res.u_calorie, "cal", 4.184),
            ConvUnit("energy.kilocalorie", Res.u_kilocalorie, "kcal", 4184.0),
            ConvUnit("energy.wattHour", Res.u_watt_hour, "Wh", 3600.0),
            ConvUnit("energy.kilowattHour", Res.u_kilowatt_hour, "kWh", 3_600_000.0),
            ConvUnit("energy.electronVolt", Res.u_electron_volt, "eV", 1.602176634e-19),
            ConvUnit("energy.btu", Res.u_btu, "BTU", 1055.05585262),
            ConvUnit("energy.footPound", Res.u_foot_pound, "ft·lb", 1.3558179483314)
        )
    )

    // Power (base: watt)
    private val power = UnitCategory(
        "power", Res.cat_power, Icons.Filled.Power,
        listOf(
            ConvUnit("power.watt", Res.u_watt, "W", 1.0),
            ConvUnit("power.kilowatt", Res.u_kilowatt, "kW", 1000.0),
            ConvUnit("power.megawatt", Res.u_megawatt, "MW", 1e6),
            ConvUnit("power.horsepower", Res.u_horsepower, "hp", 745.69987158227),
            ConvUnit("power.metricHp", Res.u_metric_hp, "PS", 735.49875),
            ConvUnit("power.btuPerHour", Res.u_btu_per_hour, "BTU/h", 0.29307107),
            ConvUnit("power.ftlbPerSec", Res.u_ftlb_per_sec, "ft·lb/s", 1.3558179483314)
        )
    )

    // Angle (base: degree)
    private val angle = UnitCategory(
        "angle", Res.cat_angle, Icons.Filled.Timeline,
        listOf(
            ConvUnit("angle.degree", Res.u_degree, "°", 1.0),
            ConvUnit("angle.radian", Res.u_radian, "rad", 57.2957795130823),
            ConvUnit("angle.gradian", Res.u_gradian, "grad", 0.9),
            ConvUnit("angle.arcminute", Res.u_arcminute, "'", 0.0166666666666667),
            ConvUnit("angle.arcsecond", Res.u_arcsecond, "\"", 0.000277777777777778),
            ConvUnit("angle.revolution", Res.u_revolution, "rev", 360.0)
        )
    )

    // Force (base: newton)
    private val force = UnitCategory(
        "force", Res.cat_force, Icons.Filled.CropSquare,
        listOf(
            ConvUnit("force.newton", Res.u_newton, "N", 1.0),
            ConvUnit("force.kilonewton", Res.u_kilonewton, "kN", 1000.0),
            ConvUnit("force.dyne", Res.u_dyne, "dyn", 1e-5),
            ConvUnit("force.poundForce", Res.u_pound_force, "lbf", 4.4482216152605),
            ConvUnit("force.kilogramForce", Res.u_kilogram_force, "kgf", 9.80665),
            ConvUnit("force.ounceForce", Res.u_ounce_force, "ozf", 0.27801385095378)
        )
    )

    // Frequency (base: hertz)
    private val frequency = UnitCategory(
        "frequency", Res.cat_frequency, Icons.Filled.AcUnit,
        listOf(
            ConvUnit("frequency.hertz", Res.u_hertz, "Hz", 1.0),
            ConvUnit("frequency.kilohertz", Res.u_kilohertz, "kHz", 1000.0),
            ConvUnit("frequency.megahertz", Res.u_megahertz, "MHz", 1e6),
            ConvUnit("frequency.gigahertz", Res.u_gigahertz, "GHz", 1e9),
            ConvUnit("frequency.rpm", Res.u_rpm, "rpm", 0.0166666666666667)
        )
    )

    // Fuel Economy (base: kilometer per liter)
    private val fuelEconomy = UnitCategory(
        "fuelEconomy", Res.cat_fuel, Icons.Filled.LocalGasStation,
        listOf(
            ConvUnit("fuelEconomy.kmPerLiter", Res.u_km_per_liter, "km/L", 1.0),
            ConvUnit("fuelEconomy.mpgUS", Res.u_mpg_us, "mpg", 0.425143707),
            ConvUnit("fuelEconomy.mpgUK", Res.u_mpg_uk, "mpg UK", 0.354006042),
            ConvUnit("fuelEconomy.milesPerLiter", Res.u_miles_per_liter, "mi/L", 1.609344)
        )
    )

    // Cooking (base: milliliter)
    private val cooking = UnitCategory(
        "cooking", Res.cat_cooking, Icons.Filled.Restaurant,
        listOf(
            ConvUnit("cooking.milliliter", Res.u_milliliter, "mL", 1.0),
            ConvUnit("cooking.liter", Res.u_liter, "L", 1000.0),
            ConvUnit("cooking.teaspoon", Res.u_teaspoon, "tsp", 4.92892159375),
            ConvUnit("cooking.tablespoon", Res.u_tablespoon, "tbsp", 14.78676478125),
            ConvUnit("cooking.cupUS", Res.u_cup_us, "cup", 236.5882365),
            ConvUnit("cooking.cupMetric", Res.u_cup_metric, "cup M", 250.0),
            ConvUnit("cooking.fluidOunce", Res.u_us_fl_oz, "fl oz", 29.5735295625),
            ConvUnit("cooking.pintUS", Res.u_us_pint, "pt", 473.176473),
            ConvUnit("cooking.quartUS", Res.u_us_quart, "qt", 946.352946),
            ConvUnit("cooking.gallonUS", Res.u_us_gallon, "gal", 3785.411784)
        )
    )
}
