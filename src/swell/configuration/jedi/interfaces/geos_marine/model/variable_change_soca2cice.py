# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------

def variable_change_soca2cice(template_dict: Mapping) -> Mapping:
    local_background_time = template_dict['local_background_time']

    variable_change_soca2cice = {
        'variable change name': 'Soca2Cice',
        'arctic': {
            'seaice edge': 0.4,
            'shuffle': True,
            'rescale prior': {
                'rescale': True,
                'min hice': 0.5,
                'min hsno': 0.1,
            }
        },
        'antarctic': {
            'seaice edge': 0.4,
            'shuffle': True,
            'rescale prior': {
                'rescale': True,
                'min hice': 0.5,
                'min hsno': 0.1,
            }
        },
        'cice background states': {
            'restart': f'iced.res.{local_background_time}.nc',
            'ncat': 5,
            'ice_lev': 7,
            'sno_lev': 1,
        },
        'cice output': {
            'restart': f'iced.res.{local_background_time}.nc'
        },
        'output variables': [
            'sea_water_potential_temperature',
            'sea_water_salinity',
            'sea_water_cell_thickness',
            'sea_ice_area_fraction',
            'sea_ice_thickness',
            'sea_ice_snow_thickness',
        ]
    }

    return variable_change_soca2cice

# --------------------------------------------------------------------------------------------------