# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_atmosphere.model.shared import \
    field_io_names, field_io_names_sa1

# --------------------------------------------------------------------------------------------------


def diffstates_output(template_dict: Mapping) -> Mapping:

    # diff states (inc)
    grid_type= template_dict['diffstates_spec_gridtype']
    prefix_output = template_dict['diffstates_spec'].get('state_diff', {}).get('fn_output')

    stateType = template_dict.get('diffstates_spec_statetype')
    if [ stateType == 'ensemble' ]:
        field_io_names_loc = field_io_names_sa1
    else:
        field_io_names_loc = field_io_names

    output = {}
    if grid_type == 'cs':
        output = {
            'filetype': 'cube sphere history',
            'provider': 'geos',
            'datapath': template_dict['cycle_dir'],
            'filename': f'{prefix_output}.%yyyy%mm%dd_%hh%MM%ssz.nc4',
            'field io names': field_io_names_loc
        }
    elif grid_type == 'latlon':
        output = {
            'filetype': 'auxgrid',
            'gridtype': 'latlon',
            'datapath': template_dict['cycle_dir'],
            'filename': f'{prefix_output}.ll.',
            'field io names': field_io_names_loc
        }

    return output

# --------------------------------------------------------------------------------------------------
