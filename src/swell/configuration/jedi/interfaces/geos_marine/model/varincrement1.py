# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------

def varincrement1(template_dict: Mapping) -> Mapping:
    varincrement1 = {
        'write increment': True,
        'increment': {
            'state component': {
                'datadir': './',
                'date': template_dict['window_begin_iso'],
                'exp': template_dict['experiment_id'],
                'type': 'incr'
            }
        }
    }

    return varincrement1

# --------------------------------------------------------------------------------------------------