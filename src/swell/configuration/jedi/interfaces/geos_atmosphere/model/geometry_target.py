# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def geometry_target(template_dict: Mapping) -> Mapping:
    """Target geometry for fv3jedi_convertstate.x.

    Uses target_horizontal_resolution from the template dictionary to describe
    the desired output horizontal resolution. Vertical resolution is unchanged
    (convert state only regrid horizontally). The processor layout is identical
    to that of the input geometry.
    """

    npx_proc = template_dict['npx_proc']
    npy_proc = template_dict['npy_proc']

    target_horizontal_resolution = template_dict['target_horizontal_resolution']
    # Vertical resolution is unchanged by convert state — input and output share the same levels.
    vertical_resolution = template_dict['vertical_resolution']

    geometry_target = {
        'fms initialization': {
            'namelist filename': './fv3-jedi/fv3files/fmsmpp.nml',
            'field table filename': './fv3-jedi/fv3files/field_table_gmao'
        },
        'akbk': f'./fv3-jedi/fv3files/akbk{vertical_resolution}.nc4',
        'layout': [npx_proc, npy_proc],
        'npx': target_horizontal_resolution,
        'npy': target_horizontal_resolution,
        'npz': vertical_resolution
    }

    return geometry_target

# --------------------------------------------------------------------------------------------------
