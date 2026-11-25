# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from swell.utilities.oops_config import OopsConfig

# --------------------------------------------------------------------------------------------------


class variational4D(OopsConfig):

    def render_oops(self):

        # For GEOS atmosphere the Identity linear model must step with the PSEUDO model
        # (background frequency), otherwise the TL/AD GetValues times do not match the
        # trajectory. Other interfaces keep their established 1-hour step.
        linear_model_tstep = 'PT1H'
        cost_type = '4D-Var'
        if self.jedi_interface == 'geos_atmosphere':
            linear_model_tstep = self.template_dict.get('background_frequency', 'PT1H')
            # PSEUDO model + Identity linear model is 3D-FGAT. With '4D-Var' the final
            # trajectory is re-read from the background files, so the analysis states after
            # the window begin and the O-A departures miss the increment; '3D-FGAT' adds the
            # increment at every time of the window.
            cost_type = '3D-FGAT'

        oops = {
            'cost function': {
                'cost type': cost_type,
                'jb evaluation': False,
                'time window': {
                    'begin': self.template_dict['window_begin_iso'],
                    'length': self.template_dict['window_length'],
                    'bound to include': 'begin'
                },
                'geometry': self.interface_model('geometry'),
                'model': self.interface_model('pseudo_model'),
                'variable change': {'variable change name': 'Analysis2Model'},
                'forecast length': self.template_dict['forecast_length'],
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
                    'linear model': {
                        'name': 'Identity',
                        'increment variables': self.template_dict['analysis_variables'],
                        'variable change': 'Identity',
                        'tstep': linear_model_tstep
                    },
                    'diagnostics': {'departures': 'ombg'},
                    'online diagnostics': self.interface_model('varincrement1')
                }]
            },
            'final': {
                'diagnostics': {
                    'departures': 'oman'
                },
                'prints': {
                    'frequency': 'PT3H'
                }
            },
            'output': self.interface_model('analysis')
        }

        return oops


# --------------------------------------------------------------------------------------------------
