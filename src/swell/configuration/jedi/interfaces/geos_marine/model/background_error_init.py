# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------

def background_error_init(template_dict: Mapping) -> Mapping:
    background_error_init = {
        'covariance model': 'SocaError',
        'analysis variables': template_dict['analysis_variables'],
        'date': template_dict['local_background_time_iso'],
        'bump': {
            'io': {'data directory': '{cycle_dir}/background_error_mode'.format(**template_dict)},
            'drivers': {
                'multivariate strategy': 'univariate',
                'compute nicas': True,
                'write local nicas': True
            },
            'model': {'do not cross mask boundaries': True},
            'nicas': {'resolution': 6.0},
        },
        'correlation': [
            {'name': 'ocn',
             'base value': 840336.134453782,
             'rossby mult': 0.280112045,
             'variables': [
                'sea_water_salinity',
                'sea_water_potential_temperature',
                'sea_surface_height_above_geoid',
                'sea_water_cell_thickness',
             ]},
             {'name': 'ice',
              'base value': 560224.089635854,
              'variables': [
                  'sea_ice_area_fraction',
                  'sea_ice_thickness',
                  'sea_ice_snow_thickness'
                  ]}
        ]
    }

    return background_error_init

# --------------------------------------------------------------------------------------------------