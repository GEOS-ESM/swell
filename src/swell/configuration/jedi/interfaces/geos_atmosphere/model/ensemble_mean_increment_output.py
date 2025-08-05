# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_atmosphere.model.shared import field_io_names_ensemble

# --------------------------------------------------------------------------------------------------

def ensemble_mean_increment_output(template_dict: Mapping) -> Mapping:

    cycle_dir = template_dict['cycle_dir']

    ensemble_mean_increment_output = {
        'filetype': 'auxgrid',
        'gridtype': 'latlon',
        'filename': f'{cycle_dir}/geos.mean-inc',
        'field io names': field_io_names_ensemble
    }

    return ensemble_mean_increment_output

# --------------------------------------------------------------------------------------------------