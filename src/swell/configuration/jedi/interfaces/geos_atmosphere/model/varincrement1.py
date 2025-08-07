# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------

def varincrement1(template_dict: Mapping) -> Mapping:

    experiment_id = template_dict['experiment_id']

    varincrement1 = {
        'write increment': True,
        'increment': {
            'state component': {
                'filetype': 'auxgrid',
                'gridtype': 'latlon',
                'datapath': './',
                'filename': f'{experiment_id}.increment-iter1.',
                'field io names': {
                    'eastward_wind': 'ua',
                    'northward_wind': 'va',
                    'air_temperature': 't',
                    'water_vapor_mixing_ratio_wrt_moist_air': 'q',
                    'cloud_liquid_ice': 'qi',
                    'cloud_liquid_water': 'ql',
                    'rain_water': 'qr',
                    'snow_water': 'qs',
                    'mole_fraction_of_ozone_in_air': 'o3ppmv',
                    'geopotential_height_times_gravity_at_surface': 'phis',
                    'skin_temperature_at_surface': 'ts',
                    'air_pressure_at_surface': 'ps',
                    }
            }
        }
    }

    return varincrement1

# --------------------------------------------------------------------------------------------------
