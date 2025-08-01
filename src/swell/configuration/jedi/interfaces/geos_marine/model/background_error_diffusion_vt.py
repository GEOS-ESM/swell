# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------

def background_error_diffusion_vt(template_dict: Mapping) -> Mapping:
    background_error_diffusion_vt = {
        'covariance model': 'SABER',
        'saber central block': {
            'saber block name': 'diffusion',
            'calibration': {
                'normalization': {
                    'method': 'randomization',
                    'iterations': 1000
                },
                'groups': [
                    {'name': 'diffusion_vt',
                     'vertical': {
                         'model file': {
                             'date': template_dict['local_background_time_iso'],
                             'basename': './',
                             'ocn_filename': 'calculated_scales.nc'
                         },
                         'model variable': 'sea_water_potential_temperature'
                     },
                     'write': {
                         'filepath': 'background_error_model/vt.{local_background_time}'.format(**template_dict)
                     }}
                ]
            }
        }
    }

    return background_error_diffusion_vt

# --------------------------------------------------------------------------------------------------