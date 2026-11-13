# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_atmosphere.model.shared import \
        state_variables, field_io_names

# --------------------------------------------------------------------------------------------------


def state_ensemble(template_dict: Mapping) -> Mapping:

    # full fname including subdir path
    fn_input = template_dict['ensmeanvariance_spec_item'].get('fn_input')

    state_ensemble_dict = {
        'members from template': {
            'template': {
                'datetime': template_dict['local_background_time_iso'],
                'filetype': 'cube sphere history',
                'provider': 'geos',
                'compute edge pressure from surface pressure': True,
                'max allowable geometry difference': 1e-3,
                'datapath': template_dict['cycle_dir'],
                'filename': fn_input,
                'state variables': state_variables,
                'field io names': field_io_names
            },
            'pattern': '%mem%',
            'nmembers': template_dict['ensemble_num_members'],
            'zero padding': 3
        }
    }

    return state_ensemble_dict

# --------------------------------------------------------------------------------------------------
