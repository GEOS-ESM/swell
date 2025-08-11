# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def geometry(template_dict: Mapping) -> Mapping:

    npx_proc = template_dict['npx_proc']
    npy_proc = template_dict['npy_proc']

    horizontal_resolution = template_dict['horizontal_resolution']
    vertical_resolution = template_dict['vertical_resolution']

    try:
        horizontal_resolution = int(horizontal_resolution)
    except ValueError:
        pass

    try:
        vertical_resolution = int(vertical_resolution)
    except ValueError:
        pass

    geometry = {
        'fms initialization': {
            'namelist filename': './fv3-jedi/fv3files/fmsmpp.nml',
            'field table filename': './fv3-jedi/fv3files/field_table_gmao'
        },
        'akbk': f'./fv3-jedi/fv3files/akbk{vertical_resolution}.nc4',
        'layout': [npx_proc, npy_proc],
        'npx': horizontal_resolution,
        'npy': horizontal_resolution,
        'npz': vertical_resolution
    }

    return geometry

# --------------------------------------------------------------------------------------------------
