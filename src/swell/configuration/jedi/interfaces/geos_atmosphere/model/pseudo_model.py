# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_atmosphere.model.shared import field_io_names

# --------------------------------------------------------------------------------------------------

def pseudo_model(template_dict: Mapping) -> Mapping:
    horizontal_resolution = template_dict['horizontal_resolution']

    pseudo_model = {
        'name': 'PSEUDO',
        'tstep': template_dict['background_frequency'],
        'filetype': 'cube sphere history',
        'provider': 'geos',
        'datapath': template_dict['cycle_dir'],
        'filenames': [
            'bkg.%yyyy%mm%ddT%hh%MM%ssZ.nc4',
            f'fv3-jedi/bkg/geos.crtmsrf.{horizontal_resolution}.nc4'
        ],
        'field io names': field_io_names
    }

    return pseudo_model

# --------------------------------------------------------------------------------------------------