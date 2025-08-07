# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from swell.utilities.oops_config import OopsConfig

# --------------------------------------------------------------------------------------------------


class fgat(OopsConfig):

    def render_oops(self):

        oops = {
            'cost function': {
                'cost type': '3D-FGAT',
                'jb evaluation': False,
                'time window': {
                    'begin': self.template_dict['window_begin_iso'],
                    'end': self.template_dict['window_end_iso'],
                    'bound to include': 'begin',
                },
                'geometry': self.interface_model('geometry'),
                'analysis variables': self.template_dict['analysis_variables'],
                'model': self.interface_model('pseudo_model'),
                'background': self.interface_model('background'),
                'background error': self.interface_model('background_error'),
                'observations': {
                    'observers': self.special_observations()
                }
            },
            'variational': {
                'minimizer': {
                    'algorithm': self.template_dict['minimizer']
                },
                'iterations': [
                    {'geometry': 'geometry_inner',
                     'gradient norm reduction': self.template_dict['gradient_norm_reduction'],
                     'ninner': str(self.template_dict['number_of_iterations']),
                     'diagnostics': {'departures': 'ombg'},
                     'online diagnostics': self.interface_model('varincrement1')}
                ]
            },
            'final': {
                'diagnostics': {'departures': 'oman'},
                'prints': {'frequency': 'PT3H'},
            },
            'output': self.interface_model('analysis')
        }

        return oops


# --------------------------------------------------------------------------------------------------
