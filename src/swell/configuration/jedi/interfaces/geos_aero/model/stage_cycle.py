# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def stage_cycle(template_dict: Mapping) -> Mapping:

    """Stage cycle-dependent files for the geos_aero interface.

    This currently mirrors the behavior of the static ``stage`` function by
    linking the FV3-JEDI FV3 files into the cycle directory. Additional
    cycle-dependent staging (e.g. aerosol-specific static data) can be added
    here as needed.
    """

    cycle_dir = template_dict['cycle_dir']
    swell_static_files = template_dict['swell_static_files']
    vertical_resolution = template_dict['vertical_resolution']
    horizontal_resolution = template_dict['horizontal_resolution']

    # Note: ``vertical_resolution`` and ``horizontal_resolution`` are
    # currently unused but kept for consistency with other interfaces and
    # future extension.
    _ = vertical_resolution
    _ = horizontal_resolution

    stage_cycle = [
        {
            'link_files': {
                'directories': [
                    [
                        f'{swell_static_files}/jedi/interfaces/geos_atmosphere/fv3files/*',
                        f'{cycle_dir}/fv3-jedi/fv3files/'
                    ],
                ]
            }
        }
    ]

    return stage_cycle

# --------------------------------------------------------------------------------------------------
