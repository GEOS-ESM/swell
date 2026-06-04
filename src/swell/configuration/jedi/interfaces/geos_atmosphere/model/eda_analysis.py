# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_atmosphere.model.shared import field_io_names
import os
# --------------------------------------------------------------------------------------------------


def eda_analysis(template_dict: Mapping) -> Mapping:

    imem = template_dict.get('ensemble_imember', None)
    analysis = {
        'filetype': 'cube sphere history',
        'provider': 'geos',
        'datapath': f'./analysis/mem{imem:03d}',
        'filename': f'{template_dict["experiment_id"]}.ana.mem{imem:03d}.%yyyy%mm%dd_%hh%MM%ssz.nc4',
        'first': 'PT0H',
        'frequency': 'PT1H',
        'field io names': field_io_names,
    }

    return analysis

# --------------------------------------------------------------------------------------------------
