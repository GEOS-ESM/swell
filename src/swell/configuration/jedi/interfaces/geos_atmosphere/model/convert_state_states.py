# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_atmosphere.model.shared import (
    state_variables,
    field_io_names,
)
# --------------------------------------------------------------------------------------------------

# State variables to carry through the resolution conversion
state_variables = [
    'eastward_wind',
    'northward_wind',
    'air_temperature',
    'air_pressure_thickness',
    'air_pressure_at_surface',
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
    'sheleg',
    'skin_temperature_at_surface',
    'soilt',
    'soilm',
    'eastward_wind_at_surface',
    'northward_wind_at_surface',
    'mole_fraction_of_carbon_dioxide_in_air',
]

# --------------------------------------------------------------------------------------------------


def convert_state_states(template_dict: Mapping) -> list:
    """Single-state entry for fv3jedi_convertstate.x.

    Describes the input (at the original resolution) and output (at the target
    resolution) for one background file.  The background file is identified by
    background_time_iso, which is set per parallel task by
    RunJediConvertStateFv3Executable.
    """

    bkg_time_iso = template_dict['background_time_iso']
    cycle_dir = template_dict['cycle_dir']
    target_horizontal_resolution = template_dict['target_horizontal_resolution']

    # JEDI-standard input filename produced by GetBackgroundGeosExperiment
    input_filename = f'bkg.{bkg_time_iso}.nc4'

    # Output filename for the converted (target-resolution) background file.
    # The TarBackgroundGeosConvertState task reads the bkg_name_mapping.json
    # written by GetBackgroundGeosExperiment to map this back to the original
    # GEOS experiment filename when building the output tarball.
    output_filename = f'bkg_c{target_horizontal_resolution}.{bkg_time_iso}.nc4'

    states = [
        {
            'input': {
                'datetime': bkg_time_iso,
                'filetype': 'cube sphere history',
                'provider': 'geos',
                'datapath': cycle_dir,
                'filenames': [input_filename],
                'state variables': state_variables,
                'field io names': field_io_names,
            },
            'output': {
                'datetime': bkg_time_iso,
                'filetype': 'cube sphere history',
                'provider': 'geos',
                'datapath': cycle_dir,
                'filenames': [output_filename],
                'state variables': state_variables,
                'field io names': field_io_names,
            },
        }
    ]

    return states

# --------------------------------------------------------------------------------------------------
