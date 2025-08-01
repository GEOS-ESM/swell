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
                 logger,
                 jedi_interface: str,
                 template_dict: Mapping,
                 window_type: str,
                 obs: list,
                 cycle_time,
                 jedi_forecast_model: str,
                 observing_system_records_path: str) -> str:
        
        self.logger = logger
        self.jedi_interface = jedi_interface
        self.template_dict = template_dict
        self.window_type = window_type
        self.obs = obs
        self.cycle_time = cycle_time
        self.jedi_forecast_model = jedi_forecast_model
        self.observing_system_records_path = observing_system_records_path

    def render_interface_observations(self, config_name: str) -> dict:

        # Assert that there is a jedi interface associated with the task
        self.logger.assert_abort(self.jedi_interface is not None, f'In order to render a ' +
                                 f'jedi interface config file the task must have an associated' +
                                 f'jedi interface.')
        
        # Path to configuration file
        config_file = os.path.join(self.jedi_config_path, 'interfaces', self.jedi_interface,
                                   'observations', f'{config_name}.yaml')
        
        # Check that the self.observing_system_records_path was set
        if self.observing_system_records_path is not None:

            # Check that observing_system_records_path and cycle_time are set
            self.logger.assert_abort(self.cycle_time is not None, f'cycle_time must be set.')

            # Check that the config_name is not ufo_tests
            if config_name != 'ufo_tests':

                # Get available and active channels
                avail_channels, active_channels = get_channels(self.observing_system_records_path,
                                                               config_name, self.cycle_time,
                                                               self.logger)

                # Add available and active channels to template dictionary
                # If config_name contains a hyphen, remove for jinja2 templating
                new_config_name = config_name.replace('-', '')
                self.template_dict[f'{new_config_name}_avail_channels'] = avail_channels
                self.template_dict[f'{new_config_name}_active_channels'] = active_channels
    
        return self.__open_file_render_to_dict__(config_file)
    
    def __open_file_render_to_dict__(self, config_file):

        # Check that config file exists
        self.logger.assert_abort(os.path.exists(config_file), f'In open_file_and_render failed ' +
                                 f'to find file \'{config_file}\'')

        # Open file as a string
        with open(config_file, 'r') as config_file_open:
            config_file_str_templated = config_file_open.read()

        # Fill templates in the configuration file using the config
        config_file_str = template_string_jinja2(self.logger, config_file_str_templated,
                                                 self.template_dict)

        # Convert string to dictionary
        return yaml.safe_load(config_file_str)


    def special_observations(self) -> Mapping:
        observations = []
        obs_list = self.obs.copy()
        for ob in obs_list:
            obs_dict = self.render_interface_observations(ob)
            use_observation = check_obs(self.observing_system_records_path, ob, obs_dict, self.cycle_time)

            if use_observation:
                observations.append(obs_dict)
            else:
                self.obs.remove(ob)
        
        return observations

    def interface_model(self, config_name: str) -> Mapping:
        interface_model_path = os.path.join(get_swell_path(), 'configuration', 'jedi',
                                            'interfaces', self.jedi_interface, 'model')
        
        config_file = os.path.join(interface_model_path, f'{config_file}.py')

        if not os.path.exists(config_file):
            self.logger.abort(f'Interface model file {config_file} does not exist.')
        
        module = import_module(f'swell.configuration.jedi.interfaces.{self.jedi_interface}.model.{config_name}')

        if hasattr(module, config_name):
            config_func = getattr(module, config_name)
            if isinstance(config_func, Callable):
                config_value = config_func(self.template_dict)
            else:
                config_value = config_func
        
        return config_value
    
    def render_oops(self) -> Mapping:
        return {}

# --------------------------------------------------------------------------------------------------