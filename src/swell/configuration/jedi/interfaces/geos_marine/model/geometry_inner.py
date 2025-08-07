# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def geometry_inner(template_dict: Mapping) -> Mapping:
    geometry_inner = {
        'mom6_input_nml': 'soca/input.nml',
        'fields metadata': 'soca/fields_metadata.yaml',
        'geom_grid_file': 'INPUT/soca_gridspec.nc',
    }

    return geometry_inner

# --------------------------------------------------------------------------------------------------
