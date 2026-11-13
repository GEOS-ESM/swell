# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_atmosphere.model.shared import \
    field_io_names, field_io_names_ensemble

# --------------------------------------------------------------------------------------------------


def comp_variance_output(template_dict: Mapping) -> Mapping:

    prefix_output_variance = template_dict['ensmeanvariance_spec_item'].get('fn_output_variance')
    state = template_dict['ensmeanvariance_spec_item'].get('state')
    grid_type = template_dict['ensmeanvariance_spec_gridtype']

    variance_output = {}
    if grid_type == 'cs':
        variance_output = {
            'filetype': 'cube sphere history',
            'provider': 'geos',
            'datapath': template_dict['cycle_dir'],
            'filename': f'{prefix_output_variance}.%yyyy%mm%dd_%hh%MM%ssz.nc4',
            'field io names': []
        }
    elif grid_type == 'latlon':
        variance_output = {
            'filetype': 'auxgrid',
            'gridtype': 'latlon',
            'datapath': template_dict['cycle_dir'],
            'filename': f'{prefix_output_variance}.ll.',
            'field io names': []
        }

    if state in ['bkg', 'analysis']:
        variance_output['field io names'] = field_io_names
    else:
        variance_output['field io names'] = field_io_names_ensemble

    return variance_output

# --------------------------------------------------------------------------------------------------
