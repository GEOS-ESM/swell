# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def increment_cs(template_dict: Mapping) -> Mapping:

    cycle_dir = template_dict['cycle_dir']

    output = {
        'state component': {
            'states': [{
                'filetype': 'cube sphere history',
                'datapath': f'{cycle_dir}',
                'filename': f'{template_dict["experiment_id"]}.inc.%yyyy%mm%dd_%hh%MM%ssz.nc4'
            }]
        }
    }

    return output

# --------------------------------------------------------------------------------------------------
