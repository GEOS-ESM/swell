# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def background_error(template_dict: Mapping) -> Mapping:

    active_variables = []
    if 'cice6' in template_dict['marine_models']:
        active_variables.extend([
            'sea_ice_area_fraction',
            'sea_ice_thickness',
            'sea_ice_snow_thickness'
        ])
    active_variables.extend([
        'sea_water_potential_temperature',
        'sea_water_salinity',
        'sea_surface_height_above_geoid'
    ])

    variables = ['sea_surface_height_above_geoid']

    if 'cice6' in template_dict['marine_models']:
        variables.extend([
            'sea_ice_area_fraction',
            'sea_ice_thickness',
            'sea_ice_snow_thickness'
        ])

    vertical_resolution = template_dict['vertical_resolution']

    try:
        vertical_resolution = int(vertical_resolution)
    except ValueError:
        pass

    background_error = {
        'covariance model': 'SABER',
        'saber central block': {
            'saber block name': 'diffusion',
            'active variables': active_variables,
            'read': {
                'groups': [
                    {'variables': [
                        'sea_water_potential_temperature',
                        'sea_water_salinity'
                        ],
                     'horizontal': {
                        # 'filepath': 'background_error_model/hz_rossby'
                        'filepath': 'background_error_model/new_corr_1p0'
                        },
                     'vertical': {
                         'levels': vertical_resolution,
                         'filepath':
                         f'background_error_model/vt.{template_dict["local_background_time"]}'
                         }
                     },
                    {'variables': variables,
                        'horizontal': {
                            # 'filepath': 'background_error_model/hz_rossby_1p5'
                            'filepath': 'background_error_model/new_corr_1p5'
                        }
                     },
                ]
                }
            },
        'date': template_dict['local_background_time_iso'],
        'saber outer blocks': [
            {'saber block name': 'SOCABkgErrFilt',
                'ocean_depth_min': 100,
                'rescale_bkgerr': 1.0,
                'efold_z': 2500.0},
            {'saber block name': 'SOCAParametricOceanStdDev',
             'temperature': {
                 'sst': {
                     'filepath': f'{template_dict["cycle_dir"]}/soca/godas_sst_bgerr.nc',
                     'variable': 'sst_bgerr'
                     },
                 },
             'unbalanced salinity': {},
             'unbalanced ssh': {},
            #  'save diagnostics': {'filepath': 'parametric_ocean_stddev_diags'}
             }
            
        ],
        'linear variable change': {
            'input variables': template_dict['analysis_variables'],
            'output variables': template_dict['analysis_variables'],
            'linear variable changes': [
                {'linear variable change name': 'BalanceSOCA',
                    'ksshts': {'nlayers': 2}}
            ]
        }
    }

    return background_error

# --------------------------------------------------------------------------------------------------
