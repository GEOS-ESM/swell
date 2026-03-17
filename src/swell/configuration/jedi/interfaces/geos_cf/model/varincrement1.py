# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_cf.model.shared import \
        field_io_names

# --------------------------------------------------------------------------------------------------


def varincrement1(template_dict: Mapping) -> Mapping:

    experiment_id = template_dict['experiment_id']

    varincrement1 = {
        'write increment': True,
        'increment': {
            'state component': {
                'filetype': 'auxgrid',
                'gridtype': 'latlon',
                'datapath': './',
                'filename': f'{experiment_id}.increment-iter1.',
                'field io names': field_io_names,
            }
        }
    }

    return varincrement1

# --------------------------------------------------------------------------------------------------
