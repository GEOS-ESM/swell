# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


FORECAST_EXPID = 'CF2'
FORECAST_TEMPLATE = '%y4%m2%d2_%h2%n2z.nc4'

# HISTORY.rc collections written by the forecast, keyed by the R2D2 file_type they are stored
# under. 'bkg' is the collection used to make backgrounds; the others are kept for diagnostics.
FORECAST_COLLECTIONS = {
    'bkg': 'jdi_inst_1hr_glo_C90x90x6_v72',
    'chm': 'chm_inst_1hr_glo_L360x181_v72',
    'met': 'met_inst_1hr_glo_L360x181_v72',
}


def forecast_history() -> Mapping:

    return {
        'expid': FORECAST_EXPID,
        'collections': FORECAST_COLLECTIONS,
        'template': FORECAST_TEMPLATE,
    }


def forecast_filename(file_time, file_type: str = 'bkg') -> str:

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

    return f'{FORECAST_EXPID}.{FORECAST_COLLECTIONS[file_type]}.{filename}'


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
                {'file_type': file_type,
                 'filename': f'{cycle_dir}/{file_type}.%Y%m%dT%H%M%SZ.nc4',
                 'r2d2_model': 'geos_cf'}
                for file_type in FORECAST_COLLECTIONS
            ]
        }
    }

    return r2d2

# --------------------------------------------------------------------------------------------------
