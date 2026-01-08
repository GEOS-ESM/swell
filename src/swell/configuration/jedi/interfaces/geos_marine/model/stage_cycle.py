# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def stage_cycle(template_dict: Mapping) -> Mapping:
    swell_static_files = template_dict['swell_static_files']
    cycle_dir = template_dict['cycle_dir']
    horizontal_resolution = template_dict['horizontal_resolution']
    vertical_resolution = template_dict['vertical_resolution']

    stage_cycle = [
        {'copy_files': {
            'directories': [
                [f'{swell_static_files}/jedi/interfaces/geos_marine/model/geometry/common/*', f'{cycle_dir}/soca/'],  # noqa
                [f'{swell_static_files}/jedi/interfaces/geos_marine/model/geometry/{horizontal_resolution}x{vertical_resolution}/socafiles/*', f'{cycle_dir}/soca/']  # noqa
            ]
        }},
        {'link_files': {
            'directories': [
                [f'{swell_static_files}/jedi/interfaces/geos_marine/model/geometry/{horizontal_resolution}x{vertical_resolution}/INPUT/*', f'{cycle_dir}/INPUT'],  # noqa
                [f'{swell_static_files}/jedi/interfaces/geos_marine/model/static_background_error/explicit_diffusion/{horizontal_resolution}x{vertical_resolution}/*', f'{cycle_dir}/background_error_model'],  # noqa
            ]
        }}
    ]

    return stage_cycle

# --------------------------------------------------------------------------------------------------
