# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------

def stage_cycle(template_dict: Mapping) -> Mapping:

    cycle_dir = template_dict['cycle_dir']
    swell_static_files = template_dict['swell_static_files']
    vertical_resolution = template_dict['vertical_resolution']
    gsibec_configuration = template_dict['gsibec_configuration']
    gsibec_nlons = template_dict['gsibec_nlons']
    gsibec_nlats = template_dict['gsibec_nlats']
    horizontal_resolution = template_dict['horizontal_resolution']

    stage_cycle = {
        'link_files': {
            'directories': [
                [f'{swell_static_files}/jedi/interfaces/geos_atmosphere/GEOS_CRTM_Surface/geos.crtmsrf.{horizontal_resolution}.nc4', f'{cycle_dir}/fv3-jedi/bkg/'],
                [f'{swell_static_files}/jedi/interfaces/geos_atmosphere/fv3files/*', f'{cycle_dir}/fv3-jedi/fv3files/'],
                [f'{swell_static_files}/jedi/interfaces/geos_atmosphere/gsibec/1.0.1/gsi-coeffs-gmao-global-l{vertical_resolution}x{gsibec_nlons}y{gsibec_nlats}.nc4', f'{cycle_dir}/fv3-jedi/gsibec/'],
                [f'{swell_static_files}/jedi/interfaces/geos_atmosphere/gsibec//1.0.1/{gsibec_configuration}_l{vertical_resolution}x{gsibec_nlons}y{gsibec_nlats}.nml', f'{cycle_dir}/fv3-jedi/gsibec/'],
                [f'{swell_static_files}/jedi/interfaces/geos_atmosphere/rcov/1.0.0/*', f'{cycle_dir}/fv3-jedi/rcov/'],
            ]
        }
    }

    return stage_cycle

# --------------------------------------------------------------------------------------------------
