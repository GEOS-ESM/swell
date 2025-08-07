# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------


def background_diffusion_vt(template_dict: Mapping) -> Mapping:
    background_diffusion_vt = {
        'date': template_dict['local_background_time_iso'],
        'read_from_file': 1,
        'basename': './',
        'ocn_filename': 'MOM6.res.{local_background_time}.nc'.format(**template_dict)
    }
    if 'cice6' in template_dict['marine_models']:
        background_diffusion_vt['ice_filename'] = 'cice.res.{local_background_time}.nc'.format(**template_dict)
    background_diffusion_vt['state variables'] = ['sea_water_potential_temperature']
    
    return background_diffusion_vt

# --------------------------------------------------------------------------------------------------
