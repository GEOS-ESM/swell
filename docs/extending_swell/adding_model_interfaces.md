# Adding a Model Interface

Model component interfaces, such as `geos_marine`, `geos_atmosphere`, and `geos_cf` are a core structural component within swell, used to set different parameters depending on workflow. 

Model interface-specific configurations live under `src/swell/configuration/jedi/interfaces/<model_component>`.

### Questions
Any questions that default to `defer_to_model` need associated values in `src/swell/configuration/jedi/interfaces/<model_component>/<suite or task>questions.yaml`. It is also possible to exclude certain questions from models using the `models` list in the question dataclass, which is useful when questions aren't relevant to all models.

### Observations
Observation configurations in JEDI are model-specific, and live under `src/swell/configuration/jedi/interfaces/<model_component>/<observation>.yaml`. These are jinja2-templated YAML files that are used in the construction of the JEDI executable config. For more information, see [Adding observations](adding_observations_and_converters.md)

### Meta files
Files under `src/swell/configuration/jedi/interfaces/<model_component>/<model_component>.yaml` set a selection of contextual information. Mainly, they are used to tell swell the specific JEDI executables that should be run for a given experiment, as well as some information about defaults.
```
jedi_interface: fv3-jedi
total_processors: 6*{{npx_proc}}*{{npy_proc}}
executables:
  ensemblehofx4D: fv3jedi_enshofx.x # PARALLEL
  # ensemblehofx3D: fv3jedi_hofx.x # SERIAL
  hofx3D: fv3jedi_hofx_nomodel.x
  hofx4D: fv3jedi_hofx.x
  variational3D: fv3jedi_var.x
  variational4D: fv3jedi_var.x
  variational4DEnsVar: fv3jedi_var.x
  localensembleda: fv3jedi_letkf.x
  ensmeanvariance: fv3jedi_ensmeanvariance.x
  obsfilters: test_ObsFilters.x
  eda3D: fv3jedi_var.x
  eda4D: fv3jedi_var.x
  diffstates: fv3jedi_diffstates.x
```

### Interface files
Swell constructs JEDI config files using the OOPS (Object Oriented Prediction System) framework. Files under `src/swell/configuration/jedi/oops` define model-agnostic programs, which then consult model-specific files to build the complete config.

```
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
                }
            },
            'output': self.interface_model('analysis')
        }

        # TODO: Implement this more cleanly in the OOPS schema
        if self.jedi_interface == 'geos_cf':
            oops['final']['increment'] = {'geometry': self.interface_model('geometry'),
                                          'output': self.interface_model('increment_cs')}

        return oops
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
                }
            },
            'output': self.interface_model('analysis')
        }

        # TODO: Implement this more cleanly in the OOPS schema
        if self.jedi_interface == 'geos_cf':
            oops['final']['increment'] = {'geometry': self.interface_model('geometry'),
                                          'output': self.interface_model('increment_cs')}

        return oops
```

`template_dict` is constructed in the swell task's `jedi_rendering` object. The method `self.interface_model` is used to point to model files under `src/swell/configuration/jedi/interfaces/<model_component>/model`
