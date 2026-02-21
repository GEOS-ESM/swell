# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_atmosphere.model.shared import field_io_names

# --------------------------------------------------------------------------------------------------


def analysis(template_dict: Mapping) -> Mapping:
    analysis = {
        'filetype': 'auxgrid',
        'gridtype': 'latlon',
        'datapath': template_dict['cycle_dir'],
        'filename': f'{template_dict["experiment_id"]}.analysis.',
#        'first': 'PT0H',
#        'frequency': 'PT1H',
        'field io names': field_io_names,
    }

    return analysis

# --------------------------------------------------------------------------------------------------
