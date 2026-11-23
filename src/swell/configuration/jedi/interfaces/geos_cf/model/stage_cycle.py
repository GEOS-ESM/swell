# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

from swell.configuration.jedi.interfaces.geos_cf.slurm import mpi_settings

# --------------------------------------------------------------------------------------------------


def stage_cycle(template_dict: Mapping) -> Mapping | list:

    cycle_dir = template_dict['cycle_dir']
    swell_static_files = template_dict['swell_static_files']
    horizontal_resolution = template_dict['horizontal_resolution']
    jedi_mpi = mpi_settings('jedi', template_dict['horizontal_resolution'],
                            template_dict.get('geos_cf_mpi'))
    npx_proc, npy_proc = jedi_mpi['nx'], jedi_mpi['ny']

    stage_cycle = [
        {'copy_files': {
            'directories': [
                [
                    f'{swell_static_files}/jedi/interfaces/geos_cf/fv3_files/*',
                    f'{cycle_dir}/'
                ]
            ]
        }}
    ]

    # Only link NICAS files when the central block corresponds to BUMP_NICAS
    central_block_select = template_dict.get('saber_central_block', 'none')
    if central_block_select == 'bump_nicas':
        stage_cycle.append({
            'link_files': {
                'directories': [
                    [
                        f'{swell_static_files}/jedi/interfaces/geos_cf/nicas/'
                        f'layout_{npx_proc}x{npy_proc}x6_{horizontal_resolution}/*',
                        f'{cycle_dir}/'
                    ]
                ]
            }
        })

    return stage_cycle

# --------------------------------------------------------------------------------------------------
