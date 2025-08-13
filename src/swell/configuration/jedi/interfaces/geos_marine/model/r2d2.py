# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def r2d2(template_dict: Mapping) -> Mapping:
    cycle_dir = template_dict['cycle_dir']
    local_background_time = template_dict['local_background_time']
    experiment_id = template_dict['experiment_id']
    analysis_time_iso = template_dict['analysis_time_iso']

    fc_list = [{'file_type': 'MOM.res',
                'filename': f'{cycle_dir}/MOM6.res.{local_background_time}.nc'}]

    if 'cice6' in template_dict['marine_models']:
        fc_list.append({'file_type': 'cice.res',
                        'filename': f'{cycle_dir}/cice.res.{local_background_time}.nc'})

    an_list = [{'file_type': 'ocn.incr',
                'filename': f'{cycle_dir}/mom6_increment.nc'}]

    if 'cice6' in template_dict['marine_models']:
        an_list.append({'file_type': 'ice.incr',
                        'filename': f'{cycle_dir}/ice.{experiment_id}.incr.{analysis_time_iso}.nc'})

    r2d2 = {
        'fetch': {
            'fc': fc_list
        },
        'store': {
            'an': an_list,
            'fc': fc_list
        }
    }

    return r2d2

# --------------------------------------------------------------------------------------------------
