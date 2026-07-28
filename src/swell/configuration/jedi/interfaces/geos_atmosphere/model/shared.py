# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

field_io_names = {
    'eastward_wind': 'ua',
    'northward_wind': 'va',
    'air_temperature': 't',
    'air_pressure_at_surface': 'ps',
    'air_pressure_levels': 'pe',
    'water_vapor_mixing_ratio_wrt_moist_air': 'q',
    'cloud_liquid_ice': 'qi',
    'cloud_liquid_water': 'ql',
    'rain_water': 'qr',
    'snow_water': 'qs',
    'mole_fraction_of_ozone_in_air': 'o3ppmv',
    'geopotential_at_surface': 'phis',
    'initial_mass_fraction_of_large_scale_cloud_condensate': 'qls',
    'initial_mass_fraction_of_convective_cloud_condensate': 'qcn',
    'convective_cloud_area_fraction': 'cfcn',
    'fraction_of_ocean': 'frocean',
    'fraction_of_land': 'frland',
    'isotropic_variance_of_filtered_topography': 'varflt',
    'surface_velocity_scale': 'ustar',
    'surface_buoyancy_scale': 'bstar',
    'planetary_boundary_layer_height': 'zpbl',
    'surface_exchange_coefficient_for_momentum': 'cm',
    'surface_exchange_coefficient_for_heat': 'ct',
    'surface_exchange_coefficient_for_moisture': 'cq',
    'KCBL_before_moist': 'kcbl',
    'surface_temp_before_moist': 'tsm',
    'lower_index_where_Kh_greater_than_2': 'khl',
    'upper_index_where_Kh_greater_than_2': 'khu',
    'fraction_of_lake': 'frlake',
    'fraction_of_ice': 'frseaice',
    'skin_temperature_at_surface': 'ts',
    'eastward_wind_at_surface': 'u10m',
    'northward_wind_at_surface': 'v10m',
    # sea_surface_temperature': 'ts_found',
    # mole_fraction_of_carbon_dioxide_in_air': 'co2',
}

# --------------------------------------------------------------------------------------------------

state_variables = [
    'eastward_wind',
    'northward_wind',
    'air_temperature',
    'air_pressure_at_surface',
    'air_pressure_levels',
    'water_vapor_mixing_ratio_wrt_moist_air',
    'cloud_liquid_ice',
    'cloud_liquid_water',
    'rain_water',
    'snow_water',
    'mole_fraction_of_ozone_in_air',
    'geopotential_at_surface',
    'initial_mass_fraction_of_large_scale_cloud_condensate',
    'initial_mass_fraction_of_convective_cloud_condensate',
    'convective_cloud_area_fraction',
    'fraction_of_ocean',
    'fraction_of_land',
    'isotropic_variance_of_filtered_topography',
    'surface_velocity_scale',
    'surface_buoyancy_scale',
    'planetary_boundary_layer_height',
    'surface_exchange_coefficient_for_momentum',
    'surface_exchange_coefficient_for_heat',
    'surface_exchange_coefficient_for_moisture',
    'KCBL_before_moist',
    'surface_temp_before_moist',
    'lower_index_where_Kh_greater_than_2',
    'upper_index_where_Kh_greater_than_2',
    'fraction_of_lake',
    'fraction_of_ice',
    'vtype',
    'stype',
    'vfrac',
    'sheleg',
    'skin_temperature_at_surface',
    'soilt',
    'soilm',
    'eastward_wind_at_surface',
    'northward_wind_at_surface',
    # 'sea_surface_temperature',
    # 'mole_fraction_of_carbon_dioxide_in_air',
]

# --------------------------------------------------------------------------------------------------

field_io_names_ensemble = {
    'eastward_wind': 'ua',
    'northward_wind': 'va',
    'air_temperature': 't',
    'air_pressure_at_surface': 'ps',
    'air_pressure_levels': 'pe',
    'water_vapor_mixing_ratio_wrt_moist_air': 'q',
    'cloud_liquid_ice': 'qi',
    'cloud_liquid_water': 'ql',
    'mole_fraction_of_ozone_in_air': 'o3ppmv',
}

# --------------------------------------------------------------------------------------------------
