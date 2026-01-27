# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def stage_cycle(template_dict: Mapping) -> Mapping:

    cycle_dir = template_dict['cycle_dir']
    swell_static_files = template_dict['swell_static_files']

    stage_cycle = {
        'copy_files': {
            'directories': [
                #[f'{swell_static_files}/jedi/interfaces/geos_cf/namelists/*', f'{cycle_dir}/']
                [f'{swell_static_files}/jedi/interfaces/geos_atmosphere/fv3files/*', f'{cycle_dir}/fv3-jedi/fv3files/'],  # noqa
                ['/gpfsm/dnb33/mabdiosk/SWELL_uv/swell/src/swell/configuration/jedi/interfaces/geos_cf/namelists/*', f'{cycle_dir}/']
            ]
        }
    }

    return stage_cycle

# --------------------------------------------------------------------------------------------------
