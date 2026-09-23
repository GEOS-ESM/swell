# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------

state_variables_to_inverse = [
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
    'fraction_of_ocean',
    'fraction_of_lake',
    'fraction_of_ice',
    'geopotential_at_surface',
    'skin_temperature_at_surface',
]

# --------------------------------------------------------------------------------------------------


def background_error_eda_gsiB(template_dict: Mapping) -> Mapping:
    vertical_resolution = template_dict['vertical_resolution']
    gsibec_nlons = template_dict['gsibec_nlons']
    gsibec_nlats = template_dict['gsibec_nlats']
    gsibec_configuration = template_dict['gsibec_configuration']
    gsibec_npx_proc = template_dict['gsibec_npx_proc']
    gsibec_npy_proc = template_dict['gsibec_npy_proc']

    background_error = {
        'covariance model': 'SABER',
        'covariance type': 'gsi hybrid covariance',
        'saber central block': {
            'saber block name': 'gsi hybrid covariance',
            'read': {
                'gsi akbk': f'./fv3-jedi/fv3files/akbk{vertical_resolution}.nc4',
                'gsi error covariance file':
                f'./fv3-jedi/gsibec/gsi-coeffs-gmao-global-l{vertical_resolution}x{gsibec_nlons}y{gsibec_nlats}.nc4',  # noqa
                'gsi berror namelist file':
                f'./fv3-jedi/gsibec/{gsibec_configuration}_l{vertical_resolution}x{gsibec_nlons}y{gsibec_nlats}.nml',  # noqa
                'processor layout x direction': gsibec_npx_proc,
                'processor layout y direction': gsibec_npy_proc,
                'debugging mode': False
            }
        },
        'saber outer blocks': [
            {'saber block name': 'interpolation',
             'inner geometry': {
                 'function space': 'StructuredColumns',
                 'custom grid matching gsi': {
                     'type': 'latlon',
                     'lats': int(gsibec_nlats),
                     'lons': int(gsibec_nlons),
                 },
                 'custom partitioner matching gsi': {
                     'bands': gsibec_npy_proc
                 },
                 'halo': 1,
             },
             'forward interpolator': {
                 'local interpolator type': 'oops unstructured grid interpolator',
             },
             'inverse interpolator': {
                 'local interpolator type': 'oops unstructured grid interpolator',
             },
             'state variables to inverse': state_variables_to_inverse}
        ],
        'linear variable change': {
            'linear variable change name': 'Control2Analysis',
            'input variables': state_variables_to_inverse,
            'output variables': template_dict['analysis_variables']
        }
    }

    return background_error

# --------------------------------------------------------------------------------------------------
