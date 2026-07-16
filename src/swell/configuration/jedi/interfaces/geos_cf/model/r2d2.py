# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


FORECAST_EXPID = 'CF2'
FORECAST_COLLECTION = 'geoscf_jedi'
FORECAST_TEMPLATE = '%y4%m2%d2T%h2%n200Z.nc4'


def forecast_history() -> Mapping:

    return {
        'expid': FORECAST_EXPID,
        'collection': FORECAST_COLLECTION,
        'template': FORECAST_TEMPLATE,
    }


def forecast_filename(file_time) -> str:

    filename = FORECAST_TEMPLATE
    replacements = {
        '%y4': file_time.strftime('%Y'),
        '%m2': file_time.strftime('%m'),
        '%d2': file_time.strftime('%d'),
        '%h2': file_time.strftime('%H'),
        '%n2': file_time.strftime('%M'),
        '%s2': file_time.strftime('%S'),
    }

    for token, value in replacements.items():
        filename = filename.replace(token, value)

    return f'{FORECAST_EXPID}.{FORECAST_COLLECTION}.{filename}'


def r2d2(template_dict: Mapping) -> Mapping:

    cycle_dir = template_dict['cycle_dir']

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
                {'file_type': 'bkg',
                 'r2d2_model': 'geos_cf'}
            ]
        }
    }

    return r2d2

# --------------------------------------------------------------------------------------------------
