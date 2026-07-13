# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_atmosphere.model.shared import field_io_names

# --------------------------------------------------------------------------------------------------


def eda_analysis_control_pert(template_dict: Mapping) -> Mapping:

    ichunk = template_dict.get('ensemble_ichunk', None)
    analysis = {
        'filetype': 'cube sphere history',
        'provider': 'geos',
        'datapath': f'./analysis_chunk/chunk{ichunk:03d}/mem%mem_pad%',
        'filename': 'eda.ana.mem%mem_pad%.%yyyy%mm%dd_%hh%MM%ssz.nc4',
        'first': 'PT0H',
        'frequency': 'PT1H',
        'field io names': field_io_names,
    }

    return analysis

# --------------------------------------------------------------------------------------------------
