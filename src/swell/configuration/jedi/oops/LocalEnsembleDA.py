# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from swell.utilities.oops_config import OopsConfig

# --------------------------------------------------------------------------------------------------

class hofx4D(OopsConfig):

    def render_oops(self):

        oops = {
            'geometry': self.template_dict('geometry'),
            'time window': {
                'begin': self.template_dict['window_begin_iso'],
                'end': self.template_dict['window_end_iso'],
                'bound to include': 'begin'
            },
            'increment variables': [
            'eastward_wind',
            'northward_wind',
            'air_temperature',
            'air_pressure_thickness',
            'water_vapor_mixing_ratio_wrt_moist_air',
            'cloud_liquid_ice',
            'cloud_liquid_water',
            'mole_fraction_of_ozone_in_air',
            ],
            'background': self.interface_model('background_ensemble'),
            'observations': {
                'get values': self.interface_model('getvalues'),
                'observers': self.special_observations()
            },
            'local ensemble DA': self.interface_model('ensemble_solver'),
            'driver': self.interface_model('ensemble_driver')
        }

        local_ensemble_save_posterior_mean = self.template_dict['local_ensemble_save_posterior_mean']
        local_ensemble_save_posterior_ensemble = self.template_dict['local_ensemble_save_posterior_ensemble']
        local_ensemble_save_posterior_mean_increment = self.template_dict['local_ensemble_save_posterior_mean_increment']
        local_ensemble_save_posterior_ensemble_increments = self.template_dict['local_ensemble_save_posterior_ensemble_increments']

        if local_ensemble_save_posterior_mean or local_ensemble_save_posterior_ensemble:
            if local_ensemble_save_posterior_mean and not local_ensemble_save_posterior_ensemble:
                oops['output'] = self.interface_model('ensemble_mean_output')
            if not local_ensemble_save_posterior_mean and local_ensemble_save_posterior_ensemble:
                oops['output'] = self.interface_model('ensemble_members_output')

        if local_ensemble_save_posterior_mean_increment:
            oops['output increment'] = self.interface_model('ensemble_mean_increment_output')
        if local_ensemble_save_posterior_ensemble_increments:
            oops['output ensemble increments'] = self.interface_model('ensemble_members_increment_output')

        return oops


# --------------------------------------------------------------------------------------------------
