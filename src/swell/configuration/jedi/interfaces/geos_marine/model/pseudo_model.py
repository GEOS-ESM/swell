# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def pseudo_model(template_dict: Mapping) -> Mapping:
    pseudo_model = {
        'name': 'PseudoModel',
        'tstep': template_dict['background_frequency'],
        'states': template_dict['states'],
    }

    return pseudo_model

# --------------------------------------------------------------------------------------------------
