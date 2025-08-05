# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_atmosphere.model.shared import field_io_names_ensemble

# --------------------------------------------------------------------------------------------------

def ensemble_driver(template_dict: Mapping) -> Mapping:

    ensemble_driver = {
        'save posterior mean': template_dict['local_ensemble_save_posterior_mean'],
        'save posterior ensemble': template_dict['local_ensemble_save_posterior_ensemble'],
        'save posterior mean increment': template_dict['local_ensemble_save_posterior_mean_increment'],
        'save posterior ensemble increments': template_dict['local_ensemble_save_posterior_ensemble_increments'],
    }

    return ensemble_driver

# --------------------------------------------------------------------------------------------------