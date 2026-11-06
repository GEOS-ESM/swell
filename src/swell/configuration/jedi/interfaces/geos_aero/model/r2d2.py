# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def r2d2(template_dict: Mapping) -> Mapping:

    cycle_dir = template_dict['cycle_dir']

    r2d2 = {
        'fetch': {
            'an': [
                {'file_type': 'bkg',
                 'r2d2_model': 'geos',
                 'filename': f'{cycle_dir}/bkg.%Y%m%dT%H%M%SZ.nc4'}
            ],
            'fc': [
                {'file_type': 'bkg',
                 'r2d2_model': 'geos',
                 'filename': f'{cycle_dir}/bkg.%Y%m%dT%H%M%SZ.nc4'}
            ]
        },
        'store': {
            'fc': [
                {'file_type': 'bkg',
                 'r2d2_model': 'geos'}
            ]
        }
    }

    return r2d2

# --------------------------------------------------------------------------------------------------
