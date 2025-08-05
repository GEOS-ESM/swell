# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_atmosphere.model.shared import field_io_names, state_variables

# --------------------------------------------------------------------------------------------------

def background(template_dict: Mapping) -> Mapping:
    horizontal_resolution = template_dict['horizontal_resolution']

    background = {
        'datetime': template_dict['local_background_time_iso'],
        'filetype': 'cube sphere history',
        'provider': 'geos',
        'datapath': template_dict['cycle_dir'],
        'filenames': [
            f'bkg.%yyyy%mm%ddT%hh%MM%ssZ.nc4',
            f'fv3-jedi/bkg/geos.crtmsrf.{horizontal_resolution}.nc4'
        ],
        'state variables': state_variables,
        'field io names': field_io_names,
    }

    return background

# --------------------------------------------------------------------------------------------------