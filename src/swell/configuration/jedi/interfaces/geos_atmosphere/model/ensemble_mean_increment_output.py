# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def ensemble_mean_increment_output(template_dict: Mapping) -> Mapping:

    cycle_dir = template_dict['cycle_dir']

    ensemble_mean_increment_output = {
        'filetype': 'auxgrid',
        'gridtype': 'latlon',
        'filename': f'{cycle_dir}/geos.mean-inc',
        'field io names': {
            'eastward_wind': 'ua',
            'northward_wind': 'va',
            'air_temperature': 't',
            'air_pressure_at_surface': 'ps',
            'air_pressure_levels': 'pe',
            'water_vapor_mixing_ratio_wrt_moist_air': 'q',
            'cloud_liquid_ice': 'qi',
            'cloud_liquid_water': 'ql',
            'mole_fraction_of_ozone_in_air': 'o3ppmv',
        }
    }

    return ensemble_mean_increment_output

# --------------------------------------------------------------------------------------------------
