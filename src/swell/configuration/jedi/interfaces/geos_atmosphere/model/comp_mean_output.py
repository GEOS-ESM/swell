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


def comp_mean_output(template_dict: Mapping) -> Mapping:

    prefix_output_mean = template_dict['ensmeanvariance_spec_item'].get('fn_output_mean')
    state = template_dict['ensmeanvariance_spec_item'].get('state')
    grid_type = template_dict['ensmeanvariance_spec_gridtype']

    mean_output = {}
    if grid_type == 'cs':
        mean_output = {
            'filetype': 'cube sphere history',
            'provider': 'geos',
            'datapath': template_dict['cycle_dir'],
            'filename': f'{prefix_output_mean}.%yyyy%mm%dd_%hh%MM%ssz.nc4',
            'first':    'PT0H',
            'frequency': 'PT1H',
            'field io names': []
        }
    elif grid_type == 'latlon':
        mean_output = {
            'filetype': 'auxgrid',
            'gridtype': 'latlon',
            'datapath': template_dict['cycle_dir'],
            'filename': f'{prefix_output_mean}.ll.',
            'field io names': []
        }

    if state in ['bkg', 'analysis']:
        mean_output['field io names'] = field_io_names
    else:
        mean_output['field io names'] = field_io_names_ensemble

    return mean_output

# --------------------------------------------------------------------------------------------------
