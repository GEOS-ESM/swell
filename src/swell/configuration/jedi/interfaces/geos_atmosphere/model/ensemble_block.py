# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def ensemble_block(template_dict: Mapping) -> Mapping:

    fn_input = template_dict['ensmeanvariance_spec_item'].get('fn_input')

    ensemble_block = {
        'members from template': {
            'template': {
                'datetime': template_dict['local_background_time_iso'],
                'filetype': 'cube sphere history',
                'provider': 'geos',
                'compute edge pressure from surface pressure': True,
                'max allowable geometry difference': 1e-3,
                'datapath': template_dict['cycle_dir'],
                'filename': fn_input,
                'state variables': [
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
                    'geopotential_height_times_gravity_at_surface',
                    'fraction_of_ocean',
                    'fraction_of_lake',
                    'fraction_of_ice',
                    'sheleg',
                    'skin_temperature_at_surface',
                    'soilt',
                    'soilm',
                    'eastward_wind_at_surface',
                    'northward_wind_at_surface',
                    # 'sea_surface_temperature',
                    # 'mole_fraction_of_carbon_dioxide_in_air',
                ],
                'field io names': {
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
                    'geopotential_height_times_gravity_at_surface': 'phis',
                    'fraction_of_ocean': 'frocean',
                    'fraction_of_lake': 'frlake',
                    'fraction_of_ice': 'frseaice',
                    'skin_temperature_at_surface': 'ts',
                    'eastward_wind_at_surface': 'u10m',
                    'northward_wind_at_surface': 'v10m',
                    # 'sea_surface_temperature': 'ts_found',
                    # 'mole_fraction_of_carbon_dioxide_in_air': 'co2',
                }
            },
            'pattern': '%mem%',
            'nmembers': template_dict['ensemble_num_members'],
            'zero padding': 3
        }
    }

    return ensemble_block

# --------------------------------------------------------------------------------------------------
