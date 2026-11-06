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

# Native cube-sphere tag and corresponding lat-lon output grid, keyed by horizontal_resolution.
# The lat-lon grid used for the optional 'chm'/'met' diagnostic collections always follows the
# cube-sphere resolution of the run (no independent override), keeping the design simple.
# c90 ~ 1deg (360x181), c180 ~ 0.5deg (720x361), c360 ~ 0.25deg (1440x721).
# NOTE: 'c180' is defined here for forward compatibility but is not yet a selectable
# horizontal_resolution (AGCM_c180.rc/CAP_c180.rc and gcm_run_geoscf.j sbatch settings for
# c180 do not exist yet; see task_questions.yaml and prep_forecast_cf.py).
RESOLUTION_GRIDS = {
    'c90':  {'cube_tag': 'C90x90x6',   'grid_label': 'PC360x181-DC',   'im': 360,  'jm': 181},
    'c180': {'cube_tag': 'C180x180x6', 'grid_label': 'PC720x361-DC',   'im': 720,  'jm': 361},
    'c360': {'cube_tag': 'C360x360x6', 'grid_label': 'PC1440x721-DC',  'im': 1440, 'jm': 721},
}

# 'bkg' is the native-grid collection used to make backgrounds and is always written; 'chm'/'met'
# are optional lat-lon diagnostic collections, enabled via the additional_forecast_collections
# question.
OPTIONAL_COLLECTION_TYPES = ('chm', 'met')


def forecast_collections(resolution: str, additional_collections: list = None) -> Mapping:
    """Build the HISTORY.rc collection names for a given cube-sphere resolution.

    'bkg' (native grid) is always included. 'chm'/'met' (lat-lon, following the same
    resolution) are included only if present in additional_collections.
    """

    additional_collections = additional_collections or []
    grid = RESOLUTION_GRIDS[resolution]

    collections = {'bkg': f"jdi_inst_1hr_glo_{grid['cube_tag']}_v72"}
    for file_type in OPTIONAL_COLLECTION_TYPES:
        if file_type in additional_collections:
            collections[file_type] = f"{file_type}_inst_1hr_glo_L{grid['im']}x{grid['jm']}_v72"

    return collections


def forecast_history(resolution: str, additional_collections: list = None) -> Mapping:

    return {
        'expid': FORECAST_EXPID,
        'collections': forecast_collections(resolution, additional_collections),
        'template': FORECAST_TEMPLATE,
        'grid': RESOLUTION_GRIDS[resolution],
    }


def forecast_filename(file_time, resolution: str, additional_collections: list = None,
                      file_type: str = 'bkg') -> str:

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

    collection = forecast_collections(resolution, additional_collections)[file_type]
    return f'{FORECAST_EXPID}.{collection}.{filename}'


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
