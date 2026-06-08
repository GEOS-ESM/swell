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

def two_states(template_dict: Mapping) -> Mapping:
    horizontal_resolution = template_dict['horizontal_resolution']
    f1 = template_dict['diffstates_spec']['state1']['fn_input']
    f2 = template_dict['diffstates_spec']['state2']['fn_input']    

    # state1: bkg
    state1 = {
        'datetime': template_dict['local_background_time_iso'],
        'filetype': 'cube sphere history',
        'provider': 'geos',
        'datapath': template_dict['cycle_dir'],
        'filename': f1,
        'state variables': state_variables,
        'field io names': field_io_names,
    }

    # state2: analysis
    state2 = {
        'datetime': template_dict['local_background_time_iso'],
        'filetype': 'cube sphere history',
        'provider': 'geos',
        'datapath': template_dict['cycle_dir'],
        'filenames': f2,
        'state variables': state_variables,
        'field io names': field_io_names,
    }
    
    combo = {'state1': state1, 'state2': state2}
    return combo

# --------------------------------------------------------------------------------------------------
