# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

from swell.configuration.jedi.interfaces.geos_cf.model.shared import cube_sphere_npx
from swell.configuration.jedi.interfaces.geos_cf.slurm import mpi_settings

# --------------------------------------------------------------------------------------------------


def geometry(template_dict: Mapping) -> Mapping:

    horizontal_resolution = template_dict['horizontal_resolution']

    jedi_mpi = mpi_settings('jedi', horizontal_resolution, template_dict.get('geos_cf_mpi'))
    npx_proc, npy_proc = jedi_mpi['nx'], jedi_mpi['ny']

    npx = npy = cube_sphere_npx(horizontal_resolution)

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
