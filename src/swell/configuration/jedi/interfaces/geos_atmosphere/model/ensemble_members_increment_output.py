# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_atmosphere.model.shared import field_io_names_sa1

# --------------------------------------------------------------------------------------------------


def ensemble_members_increment_output(template_dict: Mapping) -> Mapping:

    cycle_dir = template_dict['cycle_dir']
    suite_name = template_dict['suite_name']

    ensemble_members_increment_output = {
        'filetype': 'auxgrid',
        'gridtype': 'latlon',
        'datapath':  f'{cycle_dir}/analysis/' + 'mem%{member}%',
        'filename': f'{suite_name}.inc.eta.',
        'field io names': field_io_names_sa1
    }

    return ensemble_members_increment_output

# --------------------------------------------------------------------------------------------------
