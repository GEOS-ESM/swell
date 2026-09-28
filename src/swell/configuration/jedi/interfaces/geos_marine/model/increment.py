# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def increment(template_dict: Mapping) -> Mapping:
    analysis_time_iso = template_dict['analysis_time_iso']
    experiment_id = template_dict['experiment_id']

    increment = {
        # This is technically not the local background time but the analysis time,
        # but it gives error otherwise
        'date': template_dict['local_background_time_iso'],
        'basename': './',
        'ocn_filename': f'ocn.{experiment_id}.incr.{analysis_time_iso}.nc',
        'ice_filename': f'ice.{experiment_id}.incr.{analysis_time_iso}.nc'
    }

    return increment

# --------------------------------------------------------------------------------------------------
