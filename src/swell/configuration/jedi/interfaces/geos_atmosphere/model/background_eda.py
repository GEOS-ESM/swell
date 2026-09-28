# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_atmosphere.model.shared import \
        field_io_names

# --------------------------------------------------------------------------------------------------

state_variables = [
    'eastward_wind',
    'northward_wind',
    'air_temperature',
    'air_pressure_at_surface',
    'air_pressure_levels',
    'water_vapor_mixing_ratio_wrt_moist_air',
    'cloud_liquid_ice',
    'cloud_liquid_water',
    'rain_water',
    'snow_water',
    'mole_fraction_of_ozone_in_air',
    'geopotential_height_times_gravity_at_surface',
    'initial_mass_fraction_of_large_scale_cloud_condensate',
    'initial_mass_fraction_of_convective_cloud_condensate',
    'convective_cloud_area_fraction',
    'fraction_of_ocean',
    'fraction_of_land',
    'isotropic_variance_of_filtered_topography',
    'surface_velocity_scale',
    'surface_buoyancy_scale',
    'planetary_boundary_layer_height',
    'surface_exchange_coefficient_for_momentum',
    'surface_exchange_coefficient_for_heat',
    'surface_exchange_coefficient_for_moisture',
    'KCBL_before_moist',
    'surface_temp_before_moist',
    'lower_index_where_Kh_greater_than_2',
    'upper_index_where_Kh_greater_than_2',
    'fraction_of_lake',
    'fraction_of_ice',
    'vtype',
    'stype',
    'vfrac',
    'sheleg',
    'skin_temperature_at_surface',
    'soilt',
    'soilm',
    'eastward_wind_at_surface',
    'northward_wind_at_surface',
    # 'sea_surface_temperature',
    # 'mole_fraction_of_carbon_dioxide_in_air',
]

# --------------------------------------------------------------------------------------------------


def background_eda(template_dict: Mapping) -> Mapping:
    horizontal_resolution = template_dict['horizontal_resolution']
    imem = template_dict['ensemble_imember']

    background = {
        'datetime': template_dict['local_background_time_iso'],
        'filetype': 'cube sphere history',
        'provider': 'geos',
        'compute edge pressure from surface pressure': True,
        'max allowable geometry difference': 1e-3,
        'datapath': template_dict['cycle_dir'],
        'filenames': [
            f'./ebkg/mem{imem:03d}/geos.mem{imem:03d}.%yyyy%mm%dd_%hh%MM%ssz.nc4',
            f'./fv3-jedi/bkg/geos.crtmsrf.{horizontal_resolution}.nc4'
        ],
        'state variables': state_variables,
        'field io names': field_io_names,
    }

    return background

# --------------------------------------------------------------------------------------------------
