# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------
from ruamel.yaml import YAML
from jinja2 import Environment
##from typing import Mapping
from collections.abc import Mapping
from swell.configuration.jedi.interfaces.geos_atmosphere.model.shared import \
    field_io_names

# --------------------------------------------------------------------------------------------------

state_variables_to_inverse = [
    'eastward_wind',
    'northward_wind',
    'air_temperature',
    'air_pressure_at_surface',
#    'air_pressure_levels',
    'water_vapor_mixing_ratio_wrt_moist_air',
    'cloud_liquid_ice',
    'cloud_liquid_water',
    'rain_water',
    'snow_water',
    'mole_fraction_of_ozone_in_air',
    'fraction_of_ocean',
    'fraction_of_lake',
    'fraction_of_ice',
    'geopotential_height_times_gravity_at_surface',
    'skin_temperature_at_surface',
]

# --------------------------------------------------------------------------------------------------

background_error_template = """
covariance model: hybrid
components:
- covariance:
    covariance model: SABER
    covariance type: gsi hybrid covariance
    saber central block:
      saber block name: gsi hybrid covariance
      read:
        gsi akbk: ./fv3-jedi/fv3files/akbk{{vertical_resolution}}.nc4
        gsi error covariance file: ./fv3-jedi/gsibec/gsi-coeffs-gmao-global-l{{vertical_resolution}}x{{gsibec_nlons}}y{{gsibec_nlats}}.nc4
        gsi berror namelist file: ./fv3-jedi/gsibec/{{gsibec_configuration}}_l{{vertical_resolution}}x{{gsibec_nlons}}y{{gsibec_nlats}}.nml
        processor layout x direction: {{gsibec_npx_proc}}
        processor layout y direction: {{gsibec_npy_proc}}
        debugging mode: false
    saber outer blocks:
    - saber block name: interpolation
      inner geometry:
        function space: StructuredColumns
        custom grid matching gsi:
          type: latlon
          lats: {{gsibec_nlats}}
          lons: {{gsibec_nlons}}
        custom partitioner matching gsi:
          bands: {{gsibec_npy_proc}}
        halo: 1
      forward interpolator:
        local interpolator type: oops unstructured grid interpolator
      inverse interpolator:
        local interpolator type: oops unstructured grid interpolator
      state variables to inverse: &bvar
        {%- for var in state_variables_to_inverse %}
          - {{ var }}
        {%- endfor %}
    linear variable change:
      linear variable change name: Control2Analysis
      input variables: *bvar
  weight:
    value: 0.1

- covariance:
    covariance model: ensemble
    members from template:
      template:
        datetime: {{ local_background_time_iso }}
        filetype: cube sphere history
        provider: geos
        state variables: *bvar
        datapath: ./ebkg/mem%mem%
        filename: geos.mem%mem%.%yyyy%mm%dd_%hh%MM%ssz.nc4
        max allowable geometry difference: 1.e-4
      pattern: '%mem%'
      nmembers: {{ ensemble_num_members }}
      zero padding: 3
    localization:
      localization method: SABER
      saber central block:
        saber block name: BUMP_NICAS
        active variables: *bvar
        read:
          general:
            universe length-scale: 2500.0e3
          drivers:
            multivariate strategy: duplicated
            compute nicas: true
          model:
            level for 2d variables: last
          nicas:
            resolution: 6
            explicit length-scales: true
            horizontal length-scale:
            - groups:
              - common
              profile:
              - 3350515.0
              - 3350515.0
              - 3350515.0
              - 3350515.0
              - 3350515.0
              - 3350515.0
              - 3350515.0
              - 3092783.0
              - 3092783.0
              - 3092783.0
              - 3092783.0
              - 2835052.0
              - 2835052.0
              - 2835052.0
              - 2577320.0
              - 2577320.0
              - 2577320.0
              - 2577320.0
              - 2577320.0
              - 2577320.0
              - 2577320.0
              - 2448454.0
              - 2319588.0
              - 2190722.0
              - 2190722.0
              - 2061856.0
              - 1804124.0
              - 1804124.0
              - 1804124.0
              - 1804124.0
              - 1804124.0
              - 1804124.0
              - 1804124.0
              - 1804124.0
              - 1804124.0
              - 1804124.0
              - 1804124.0
              - 1804124.0
              - 1675258.0
              - 1417526.0
              - 1288660.0
              - 1237113.0
              - 1185567.0
              - 1082474.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 1030928.0
              - 2030928.0
              - 2030928.0
              - 2030928.0
            vertical length-scale:
            - groups:
              - common
              value: 1.23
    linear variable change:
      linear variable change name: Control2Analysis
      input variables: *bvar
  weight:
    value: 0.9
"""


def background_error_hybrid(template_dict: Mapping) -> Mapping:
    render_context = {
        **template_dict,
        'state_variables_to_inverse': state_variables_to_inverse,
        'field_io_names': field_io_names
    }

    # initialize Jinja and render the template
    env = Environment()
    template = env.from_string(background_error_template)

    # pass the combined dictionary here
    rendered_yaml_string = template.render(**render_context)
    # Use ruamel.yaml to load the string instead of standard pyyaml
    ruamel_yaml = YAML()
    background_error = ruamel_yaml.load(rendered_yaml_string)
    cov_template = background_error['components'][1]['covariance']['members from template']['template']
    cov_template['field io names'] = field_io_names
    a = background_error['components'][0]['covariance']['linear variable change']
    a['output variables'] = template_dict['analysis_variables']
    a = background_error['components'][1]['covariance']['linear variable change']
    a['output variables'] = template_dict['analysis_variables']

    return background_error

# --------------------------------------------------------------------------------------------------
