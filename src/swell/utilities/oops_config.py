# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

import os
import yaml
from collections.abc import Mapping, Callable
from importlib import import_module

from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.get_channels import get_channels
from swell.utilities.run_jedi_executables import check_obs
from swell.swell_path import get_swell_path

# --------------------------------------------------------------------------------------------------


class OopsConfig():

    def __init__(self,
                 jedi_rendering,
                 window_type: str,
                 obs: list,
                 cycle_time,
                 jedi_forecast_model: str,
                 observing_system_records_path: str) -> str:
        
        self.jedi_rendering = jedi_rendering
        self.logger = jedi_rendering.logger
        self.jedi_interface = jedi_rendering.jedi_interface
        self.template_dict = jedi_rendering.__template_dict__
        self.window_type = window_type
        self.obs = obs
        self.cycle_time = cycle_time
        self.jedi_forecast_model = jedi_forecast_model
        self.observing_system_records_path = observing_system_records_path

        self.jedi_config_path = os.path.join(get_swell_path(), 'configuration', 'jedi')

    def special_observations(self) -> Mapping:
        observations = []
        obs_list = self.obs.copy()
        for ob in obs_list:
            obs_dict = self.jedi_rendering.render_interface_observations(ob)
            use_observation = check_obs(self.observing_system_records_path, ob, obs_dict, self.cycle_time)
            print(use_observation)
            if use_observation:
                observations.append(obs_dict)
            else:
                self.obs.remove(ob)
        
        return observations

    def interface_model(self, config_name: str) -> Mapping:
        config_value = self.jedi_rendering.render_interface_model(config_name)
        
        return config_value
    
    def render_oops(self) -> Mapping:
        return {}

# --------------------------------------------------------------------------------------------------
