# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def background(template_dict: Mapping) -> Mapping:
    background = {
        'date': template_dict['local_background_time_iso'],
        'read_from_file': 1,
        'basename': './',
        'ocn_filename': 'MOM6.res.{template_dict["local_background_time"]}.nc'
    }
    if 'cice6' in template_dict['marine_models']:
        background['ice_filename'] = 'cice.res.{template_dict["local_background_time"}.nc'

    state_variables = []
    if 'cice6' in template_dict['marine_models']:
        state_variables.extend([
            'sea_ice_area_fraction',
            'sea_ice_thickness',
            'sea_ice_snow_thickness'
        ])
    state_variables.extend([
        'sea_water_salinity',
        'sea_water_potential_temperature',
        'sea_surface_height_above_geoid',
        'sea_water_cell_thickness',
        'ocean_mixed_layer_thickness',
        'sea_water_depth'
    ])
    background['state variables'] = state_variables

    return background

# --------------------------------------------------------------------------------------------------
