# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
import yaml
from typing import Union, Optional, Any

from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.get_channels import get_channels
from swell.utilities.logger import Logger
from swell.utilities.datetime_util import Datetime

# --------------------------------------------------------------------------------------------------


class JediConfigRendering():

    def __init__(
        self,
        logger: Logger,
        experiment_root: str,
        experiment_id: str,
        cycle_dir: Optional[str],
        cycle_time: Optional[Datetime],
        jedi_interface: Optional[str] = None
    ) -> None:

        # Keep a copy of the logger
        self.logger = logger

        # Keep a copy of the cycle directory
        self.cycle_dir = cycle_dir

        # Copy the experiment configuration path
        self.jedi_config_path = os.path.join(experiment_root, experiment_id, 'configuration',
                                             'jedi')

        # Fields needed for get_active_channels
        self.cycle_time = None

        if cycle_time is not None:
            self.cycle_time = cycle_time.dto()

        self.observing_system_records_path = None

        # Dictionary to hold things that can be templated
        self.__template_dict__ = {}

        # Always store the cycle directory in the dictionary
        self.__template_dict__['cycle_dir'] = cycle_dir

        # Add the jedi interface to the dictionary
        self.jedi_interface = jedi_interface
        self.__template_dict__['model_component'] = jedi_interface

        # Add experiment info to dictionary
        self.__template_dict__['experiment_id'] = experiment_id
        self.__template_dict__['experiment_root'] = experiment_root

        # List of all potential valid keys that can be used in templates
        self.valid_template_keys = [
            'analysis_variables',
            'analysis_time',
            'analysis_time_iso',
            'background_error_model',
            'background_frequency',
            'background_time',
            'cice6_domain',
            'crtm_coeff_dir',
            'cycling_varbc',
            'ensemble_members',
            'ensemble_hofx_packets',
            'ensemble_hofx_strategy',
            'ensemble_num_members',
            'ensmean_only',
            'ensmeanvariance_only',
            'gradient_norm_reduction',
            'gsibec_configuration',
            'gsibec_npx_proc',
            'gsibec_npy_proc',
            'horizontal_localization_lengthscale',
            'horizontal_localization_max_nobs',
            'horizontal_localization_method',
            'horizontal_resolution',
            'local_background_time',
            'local_background_time_iso',
            'local_ensemble_inflation_mult',
            'local_ensemble_inflation_rtpp',
            'local_ensemble_inflation_rtps',
            'local_ensemble_save_posterior_ensemble',
            'local_ensemble_save_posterior_ensemble_increments',
            'local_ensemble_save_posterior_mean',
            'local_ensemble_save_posterior_mean_increment',
            'local_ensemble_solver',
            'local_ensemble_use_linear_observer',
            'marine_models',
            'minimizer',
            'mom6_iau',
            'npx_proc',
            'npy_proc',
            'number_of_iterations',
            'packet_ensemble_members',
            'skip_ensemble_hofx',
            'swell_static_files',
            'total_processors',
            'vertical_localization_apply_log_transform',
            'vertical_localization_function',
            'vertical_localization_ioda_vertical_coord',
            'vertical_localization_ioda_vertical_coord_group',
            'vertical_localization_lengthscale',
            'vertical_localization_method',
            'vertical_resolution',
            'window_begin',
            'window_begin_iso',
            'window_end_iso',
            'window_length',
        ]

        # List of all potential valid dynamic keys that can be used in templates
        self.valid_dynamic_keys = [
            'states',
            'mem',
        ]

    # ----------------------------------------------------------------------------------------------

    # Function to add key to the template dictionary
    def add_key(self, key: str, element: Any) -> None:

        # First assert that key is allowed
        self.logger.assert_abort(key in self.valid_template_keys, f'Trying to add key \'{key}\' ' +
                                 f'to jedi config rendering dictionary. But the key is not part ' +
                                 f'of the valid keys: \'{self.valid_template_keys}\'')

        # Add element to dictionary
        self.__template_dict__[key] = element

    # ----------------------------------------------------------------------------------------------

    # Function to add key to the template dictionary
    def add_dynamic_key(self, key, element):

        # First assert that key is allowed
        self.logger.assert_abort(key in self.valid_dynamic_keys, f'Trying to add key \'{key}\' ' +
                                 f'to jedi config rendering dictionary. But the key is not part ' +
                                 f'of the valid dynamic keys: \'{self.valid_dynamic_keys}\'')

        # Add element to dictionary
        self.__template_dict__[key] = element

    # ----------------------------------------------------------------------------------------------

    # Open the file at the provided path, use dictionary to complete templates and return dictionary
    def __open_file_render_to_dict__(self, config_file: str) -> dict[Any, Any]:

        # Check that config file exists
        self.logger.assert_abort(os.path.exists(config_file), f'In open_file_and_render failed ' +
                                 f'to find file \'{config_file}\'')

        # Open file as a string
        with open(config_file, 'r') as config_file_open:
            config_file_str_templated = config_file_open.read()

        # Fill templates in the configuration file using the config
        config_file_str = template_string_jinja2(self.logger, config_file_str_templated,
                                                 self.__template_dict__)

        # Convert string to dictionary
        return yaml.safe_load(config_file_str)

    # ----------------------------------------------------------------------------------------------

    # Prepare path to oops file and call rendering
    def render_oops_file(self, config_name: str) -> dict:

        # Path to configuration file
        config_file = os.path.join(self.jedi_config_path, 'oops', f'{config_name}.yaml')

        # Render templates in file and return dictionary
        return self.__open_file_render_to_dict__(config_file)

    # ----------------------------------------------------------------------------------------------

    # Prepare path to interface model file and call rendering
    def render_interface_model(self, config_name: str) -> dict[Any, Any]:

        # Assert that there is a jedi interface associated with the task
        self.logger.assert_abort(self.jedi_interface is not None, f'In order to render a ' +
                                 f'jedi interface config file the task must have an associated' +
                                 f'jedi interface.')

        # Path to configuration file
        config_file = os.path.join(self.jedi_config_path, 'interfaces', self.jedi_interface,
                                   'model', f'{config_name}.yaml')

        # Render templates in file and return dictionary
        return self.__open_file_render_to_dict__(config_file)

    # ----------------------------------------------------------------------------------------------

    def set_obs_records_path(self, path: str) -> None:

        # Never put a path that is string None in place
        if path == 'None':
            cd = self.cycle_dir
            self.observing_system_records_path = os.path.join(cd, 'observing_system_records')
        else:
            self.observing_system_records_path = path

    # ----------------------------------------------------------------------------------------------

    # Prepare path to interface observations file and call rendering
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
                self.__template_dict__[f'{new_config_name}_avail_channels'] = avail_channels
                self.__template_dict__[f'{new_config_name}_active_channels'] = active_channels

        # Render templates in file and return dictionary
        return self.__open_file_render_to_dict__(config_file)

    # ----------------------------------------------------------------------------------------------

    # Prepare path to interface metadata file and call rendering

    def render_interface_meta(self, model_component_in: Union[str, dict, None] = None) -> dict:

        # Optionally open a different model interface
        model_component = self.jedi_interface
        if model_component_in is not None:
            model_component = model_component_in

        # Assert that there is a jedi interface associated with the task
        self.logger.assert_abort(model_component is not None, f'In order to render a jedi ' +
                                 f'interface config file the function or object must have an ' +
                                 f'associated jedi interface.')

        # Path to configuration file
        config_file = os.path.join(self.jedi_config_path, 'interfaces', model_component,
                                   f'{model_component}.yaml')

        # Render templates in file and return dictionary
        return self.__open_file_render_to_dict__(config_file)

# --------------------------------------------------------------------------------------------------
