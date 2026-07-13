# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from swell.utilities.oops_config import OopsConfig

# --------------------------------------------------------------------------------------------------


class eda_control_pert(OopsConfig):

    def render_oops(self):
        nmember = self.template_dict['ensemble_num_members']
        nchunk = self.template_dict['ensemble_num_chunks']
        ichunk = self.template_dict['ensemble_ichunk']
        nstate = int ( nmember / nchunk )
        if ichunk == 1:
            num_pert_mem = nstate - 1
        else:
            num_pert_mem = nstate
        pert_start_index = 1

        oops = {
            'assimilation': {
              'cost function': {
                  'cost type': '3D-Var',
                  'jb evaluation': False,
                  'time window': {
                      'begin': self.template_dict['window_begin_iso'],
                      'length': self.template_dict['window_length'],
                      'bound to include': 'begin'
                  },
                  'geometry': self.interface_model('geometry'),
                  'analysis variables': self.template_dict['analysis_variables'],
                  'background': self.interface_model('background_eda_control_pert'),
                  'background error': self.interface_model('background_error_eda_gsiB'),
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
                  }],
              },
              'final': {
                  'diagnostics': {
                      'departures': 'oman'
                  },
                  'prints': {
                      'frequency': 'PT3H'
                  }
              },
              'output': self.interface_model('eda_analysis_control_pert')
            },
            'template': {
                'pattern with zero padding': "%mem_pad%",
                'pattern without zero padding': "%mem_wo_pad%",
                'number of pert members':   num_pert_mem,
                'first pert member index':  pert_start_index,
                'run pert members only': False
              }
        }

        # TODO: Implement this more cleanly in the OOPS schema
        if self.jedi_interface == 'geos_cf':
            oops['final']['increment'] = {'geometry': self.interface_model('geometry'),
                                          'output': self.interface_model('increment_cs')}

        return oops
