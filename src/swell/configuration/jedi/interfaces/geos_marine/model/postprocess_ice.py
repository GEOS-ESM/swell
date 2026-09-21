# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def postprocess_ice(template_dict: Mapping) -> Mapping:
    local_background_time = template_dict['local_background_time']

    postprocess_ice = {
        'ncat': 5,
        'ice_lev': 7,
        'sno_lev': 1,
        'cice restart': {
            'input': f'iced.res.{local_background_time}.nc',
            'output': f'iced.res.{local_background_time}.nc'
        },
        'itd': {
            'category bounds': [0.0, 0.6445072, 1.391433, 2.470179, 4.567288, 9.333887]
        }
    }

    return postprocess_ice

# --------------------------------------------------------------------------------------------------
