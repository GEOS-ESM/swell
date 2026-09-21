# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_cf.model.shared import field_io_names

# --------------------------------------------------------------------------------------------------


def pseudo_model(template_dict: Mapping) -> Mapping:

    # The PSEUDO model reads pre-computed backgrounds rather than integrating a model. GetBackground
    # stages one file per background_frequency step across the window, so tstep must match that
    # frequency and the filename template must match the r2d2 target file name.
    pseudo_model = {
        'name': 'PSEUDO',
        'tstep': template_dict['background_frequency'],
        'filetype': 'cube sphere history',
        'provider': 'geos',
        'max allowable geometry difference': 0.1,
        'datapath': template_dict['cycle_dir'],
        'filename': 'bkg.%yyyy%mm%ddT%hh%MM%ssZ.nc4',
        'field io names': field_io_names,
    }

    return pseudo_model

# --------------------------------------------------------------------------------------------------
