# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def ensemble_mean_output(template_dict: Mapping) -> Mapping:

    ensemble_mean_output = {
        'datadir': './',
        'exp': template_dict['experiment_id'],
        'type': 'an'
    }

    return ensemble_mean_output

# --------------------------------------------------------------------------------------------------
