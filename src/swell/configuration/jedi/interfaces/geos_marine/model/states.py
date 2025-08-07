# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def states(template_dict: Mapping) -> Mapping:
    experiment_id = template_dict['experiment_id']
    analysis_time_iso = template_dict['analysis_time_iso']

    input_dict = {
        'read_from_file': 1,
        'basename': './',
        'ocn_filename': f'ocn.{experiment_id}.an.{analysis_time_iso}.nc'
    }

    if 'cice6' in template_dict['marine_models']:
        input_dict['ice_filename'] = f'ice.{experiment_id}.an.{analysis_time_iso}.nc'

    input_dict['date'] = analysis_time_iso

    state_variables = [
        'sea_water_potential_temperature',
        'sea_water_salinity',
        'sea_water_cell_thickness',
    ]

    if 'cice6' in template_dict['marine_models']:
        state_variables.extend([
            'sea_ice_area_fraction',
            'sea_ice_thickness',
            'sea_ice_snow_thickness',
        ])

    input_dict['state_variables'] = state_variables

    output_dict = {
        'datadir': './',
        'exp': experiment_id,
        'type': 'fc',
        'date': template_dict['local_background_time_iso']
    }

    states = [
        {'input': input_dict,
         'output': output_dict}
    ]

    return states

# --------------------------------------------------------------------------------------------------
