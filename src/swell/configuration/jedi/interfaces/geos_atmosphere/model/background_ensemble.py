# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_atmosphere.model.shared import \
        state_variables, field_io_names

# --------------------------------------------------------------------------------------------------


def background_ensemble(template_dict: Mapping) -> Mapping:
    horizontal_resolution = template_dict['horizontal_resolution']

    background_ensemble = {
        'date': template_dict['window_begin_iso'],
        'members from template': {
            'template': {
                'datetime': template_dict['local_background_time_iso'],
                'filetype': 'cube sphere history',
                'provider': 'geos',
                'compute edge pressure from surface pressure': True,
                'max allowable geometry difference': 1e-3,
                'datapath': '.',
                'filenames': [
                    f'ebkg/mem%mem%/geos.mem%mem%.%yyyy%mm%dd_%hh%MM%ssz.nc4',
                    f'fv3-jedi/bkg/geos.crtmsrf.{horizontal_resolution}.nc4'
                ],
                'state variables': state_variables,
                'field io names': field_io_names
            },
            'pattern': '%mem%',
            'nmembers': template_dict['ensemble_num_members'],
            'zero padding': 3,
        }
    }

    return background_ensemble

# --------------------------------------------------------------------------------------------------
