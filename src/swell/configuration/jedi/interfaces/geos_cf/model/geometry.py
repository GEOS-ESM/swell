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

    npx = template_dict['npx']
    npy = template_dict['npy']

    vertical_resolution = template_dict['vertical_resolution']

    cycle_dir = template_dict['cycle_dir']

    geometry = {
        'fms initialization': {
            'namelist filename': f'{cycle_dir}/fmsmpp.nml',
            'field table filename': f'{cycle_dir}/field_table_gmao'
        },
        'akbk': f'{cycle_dir}/akbk{vertical_resolution}.nc4',
        'layout': [npx_proc, npy_proc],
        'npx': npx,
        'npy': npy,
        'npz': vertical_resolution
    }

    return geometry

# --------------------------------------------------------------------------------------------------
