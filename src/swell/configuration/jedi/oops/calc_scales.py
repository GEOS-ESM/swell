# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from swell.utilities.oops_config import OopsConfig

# --------------------------------------------------------------------------------------------------

class calc_scales(OopsConfig):

    def render_oops(self):
        local_background_time = self.template_dict['local_background_time']
        cycle_dir = self.template_dict['cycle_dir']

        oops = {
            'gridspec_filename': 'INPUT/soca_gridspec.nc',
            'restart_filename': f'MOM6.res.{local_background_time}.nc',
            'mld_filename': f'MOM6.res.{local_background_time}.nc',
            'output_filename': f'{cycle_dir}/calculated_scales.nc',

            # These names should match the model variables for now
            'output_variable_vt': 'Temp',
            'output_variable_hz': 'ave_ssh',

            # Parameters for the vertical scale
            'VT_MIN': 1.5,
            'VT_MAX': 10,

            # Parameters for the horizontal scale
            'HZ_ROSSBY_MULT': 1.0,
            'HZ_MAX': 200e3,
            'HZ_MIN_GRID_MULT': 1.0
        }

        return oops


# --------------------------------------------------------------------------------------------------
