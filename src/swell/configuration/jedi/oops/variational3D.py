# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from swell.utilities.oops_config import OopsConfig

# --------------------------------------------------------------------------------------------------


class variational3D(OopsConfig):

    def render_oops(self):
        oops = {
            'cost function': {
                'cost type': '3D-Var',
                'jb evaluation': False,
                'time window': {
                    'begin': self.template_dict['window_begin_iso'],
                    'end': self.template_dict['window_end_iso'],
                    'bound to include': 'begin'
                },
                'geometry': self.interface_model('geometry'),
                'analysis variables': self.template_dict['analysis_variables'],
                'background': self.interface_model('background'),
                'background error': self.interface_model('background_error'),
                'observations': {
                    'get values': self.interface_model('getvalues'),
                    'observers': self.special_observations(),
                }
            },
            'variational': {
                'minimizer': {
                    'algorithm': self.template_dict['minimizer']
                },
                'iterations': [{
                    'geometry': self.interface_model('geometry_inner'),
                    'gradient norm reduction': float(self.template_dict['gradient_norm_reduction']),
                    'ninner': self.template_dict['number_of_iterations'],
                    'diagnostics': {
                        'departures': 'ombg'
                    },
                    'online diagnostics': self.interface_model('varincrement1')
                }],
            },
            'final': {
                'diagnostics': {
                    'departures': 'oman'
                },
                'prints': {
                    'frequency': 'PT3H'
                },
            },
            'output': self.interface_model('analysis')
        }

        # TODO: Implement this more cleanly in the OOPS schema
        if self.jedi_interface == 'geos_cf':
            oops['final']['increment'] = {'geometry': self.interface_model('geometry'),
                                          'output': self.interface_model('increment_cs')}

        return oops


# --------------------------------------------------------------------------------------------------
