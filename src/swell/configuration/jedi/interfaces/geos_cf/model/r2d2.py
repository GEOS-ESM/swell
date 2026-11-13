# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

from swell.configuration.jedi.interfaces.geos_cf.model.shared import forecast_collections

# --------------------------------------------------------------------------------------------------


def r2d2(template_dict: Mapping, resolution: str, additional_collections: list = None) -> Mapping:

    cycle_dir = template_dict['cycle_dir']
    file_types = list(forecast_collections(resolution, additional_collections))

    r2d2 = {
        'fetch': {
            'an': [
                {'file_type': 'bkg',
                 'r2d2_model': 'geos_cf',
                 'filename': f'{cycle_dir}/bkg.%Y%m%dT%H%M%SZ.nc4'}
            ],
            'fc': [
                {'file_type': 'bkg',
                 'r2d2_model': 'geos_cf',
                 'filename': f'{cycle_dir}/bkg.%Y%m%dT%H%M%SZ.nc4'}
            ]
        },
        'store': {
            'fc': [
                {'file_type': file_type,
                 'filename': f'{cycle_dir}/{file_type}.%Y%m%dT%H%M%SZ.nc4',
                 'r2d2_model': 'geos_cf'}
                for file_type in file_types
            ]
        }
    }

    return r2d2

# --------------------------------------------------------------------------------------------------
