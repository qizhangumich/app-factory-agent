package com.appfactory.unitconverterpro.model

import com.appfactory.unitconverterpro.R

/**
 * Thin alias layer between the pure-data unit catalog and the generated [R]
 * class. Keeping the catalog referencing [Res] (rather than [R] directly) means
 * [UnitData] reads as plain data and string-resource renames stay in one place.
 */
object Res {
    // Category names
    val cat_length = R.string.cat_length
    val cat_weight = R.string.cat_weight
    val cat_temperature = R.string.cat_temperature
    val cat_speed = R.string.cat_speed
    val cat_volume = R.string.cat_volume
    val cat_area = R.string.cat_area
    val cat_data = R.string.cat_data
    val cat_time = R.string.cat_time
    val cat_pressure = R.string.cat_pressure
    val cat_energy = R.string.cat_energy
    val cat_power = R.string.cat_power
    val cat_angle = R.string.cat_angle
    val cat_force = R.string.cat_force
    val cat_frequency = R.string.cat_frequency
    val cat_fuel = R.string.cat_fuel
    val cat_cooking = R.string.cat_cooking

    // Length
    val u_kilometer = R.string.u_kilometer
    val u_meter = R.string.u_meter
    val u_centimeter = R.string.u_centimeter
    val u_millimeter = R.string.u_millimeter
    val u_micrometer = R.string.u_micrometer
    val u_nanometer = R.string.u_nanometer
    val u_mile = R.string.u_mile
    val u_yard = R.string.u_yard
    val u_foot = R.string.u_foot
    val u_inch = R.string.u_inch
    val u_nautical_mile = R.string.u_nautical_mile
    val u_light_year = R.string.u_light_year

    // Weight
    val u_metric_ton = R.string.u_metric_ton
    val u_kilogram = R.string.u_kilogram
    val u_gram = R.string.u_gram
    val u_milligram = R.string.u_milligram
    val u_microgram = R.string.u_microgram
    val u_pound = R.string.u_pound
    val u_ounce = R.string.u_ounce
    val u_stone = R.string.u_stone
    val u_short_ton = R.string.u_short_ton
    val u_long_ton = R.string.u_long_ton
    val u_carat = R.string.u_carat

    // Temperature
    val u_celsius = R.string.u_celsius
    val u_fahrenheit = R.string.u_fahrenheit
    val u_kelvin = R.string.u_kelvin

    // Speed
    val u_mps = R.string.u_mps
    val u_kmh = R.string.u_kmh
    val u_mph = R.string.u_mph
    val u_knot = R.string.u_knot
    val u_fps = R.string.u_fps
    val u_mach = R.string.u_mach

    // Volume
    val u_cubic_meter = R.string.u_cubic_meter
    val u_liter = R.string.u_liter
    val u_milliliter = R.string.u_milliliter
    val u_cubic_cm = R.string.u_cubic_cm
    val u_us_gallon = R.string.u_us_gallon
    val u_us_quart = R.string.u_us_quart
    val u_us_pint = R.string.u_us_pint
    val u_us_cup = R.string.u_us_cup
    val u_us_fl_oz = R.string.u_us_fl_oz
    val u_imp_gallon = R.string.u_imp_gallon
    val u_cubic_inch = R.string.u_cubic_inch

    // Area
    val u_sq_kilometer = R.string.u_sq_kilometer
    val u_hectare = R.string.u_hectare
    val u_sq_meter = R.string.u_sq_meter
    val u_sq_centimeter = R.string.u_sq_centimeter
    val u_sq_mile = R.string.u_sq_mile
    val u_acre = R.string.u_acre
    val u_sq_yard = R.string.u_sq_yard
    val u_sq_foot = R.string.u_sq_foot
    val u_sq_inch = R.string.u_sq_inch

    // Data
    val u_bit = R.string.u_bit
    val u_byte = R.string.u_byte
    val u_kilobit = R.string.u_kilobit
    val u_kilobyte = R.string.u_kilobyte
    val u_megabit = R.string.u_megabit
    val u_megabyte = R.string.u_megabyte
    val u_gigabit = R.string.u_gigabit
    val u_gigabyte = R.string.u_gigabyte
    val u_terabyte = R.string.u_terabyte
    val u_petabyte = R.string.u_petabyte

    // Time
    val u_nanosecond = R.string.u_nanosecond
    val u_microsecond = R.string.u_microsecond
    val u_millisecond = R.string.u_millisecond
    val u_second = R.string.u_second
    val u_minute = R.string.u_minute
    val u_hour = R.string.u_hour
    val u_day = R.string.u_day
    val u_week = R.string.u_week
    val u_month = R.string.u_month
    val u_year = R.string.u_year

    // Pressure
    val u_pascal = R.string.u_pascal
    val u_kilopascal = R.string.u_kilopascal
    val u_bar = R.string.u_bar
    val u_psi = R.string.u_psi
    val u_atmosphere = R.string.u_atmosphere
    val u_torr = R.string.u_torr
    val u_mmhg = R.string.u_mmhg

    // Energy
    val u_joule = R.string.u_joule
    val u_kilojoule = R.string.u_kilojoule
    val u_calorie = R.string.u_calorie
    val u_kilocalorie = R.string.u_kilocalorie
    val u_watt_hour = R.string.u_watt_hour
    val u_kilowatt_hour = R.string.u_kilowatt_hour
    val u_electron_volt = R.string.u_electron_volt
    val u_btu = R.string.u_btu
    val u_foot_pound = R.string.u_foot_pound

    // Power
    val u_watt = R.string.u_watt
    val u_kilowatt = R.string.u_kilowatt
    val u_megawatt = R.string.u_megawatt
    val u_horsepower = R.string.u_horsepower
    val u_metric_hp = R.string.u_metric_hp
    val u_btu_per_hour = R.string.u_btu_per_hour
    val u_ftlb_per_sec = R.string.u_ftlb_per_sec

    // Angle
    val u_degree = R.string.u_degree
    val u_radian = R.string.u_radian
    val u_gradian = R.string.u_gradian
    val u_arcminute = R.string.u_arcminute
    val u_arcsecond = R.string.u_arcsecond
    val u_revolution = R.string.u_revolution

    // Force
    val u_newton = R.string.u_newton
    val u_kilonewton = R.string.u_kilonewton
    val u_dyne = R.string.u_dyne
    val u_pound_force = R.string.u_pound_force
    val u_kilogram_force = R.string.u_kilogram_force
    val u_ounce_force = R.string.u_ounce_force

    // Frequency
    val u_hertz = R.string.u_hertz
    val u_kilohertz = R.string.u_kilohertz
    val u_megahertz = R.string.u_megahertz
    val u_gigahertz = R.string.u_gigahertz
    val u_rpm = R.string.u_rpm

    // Fuel Economy
    val u_km_per_liter = R.string.u_km_per_liter
    val u_mpg_us = R.string.u_mpg_us
    val u_mpg_uk = R.string.u_mpg_uk
    val u_miles_per_liter = R.string.u_miles_per_liter

    // Cooking
    val u_teaspoon = R.string.u_teaspoon
    val u_tablespoon = R.string.u_tablespoon
    val u_cup_us = R.string.u_cup_us
    val u_cup_metric = R.string.u_cup_metric
}
