# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.utilities.jinja2 import template_string_jinja2


# --------------------------------------------------------------------------------------------------

class JediConfigRendering():

    def __init__(self, logger, experiment_root, experiment_id, cycle_dir, jedi_interface=None):

        # Keep a copy of the logger
        self.logger = logger

        # Copy the experiment configuration path
        self.jedi_config_path = os.path.join(experiment_root, experiment_id, 'configuration',
                                             'jedi')

        # Dictionary to hold things that can be templated
        self.template_dict = {}

        # Always store the cycle directory in the dictionary
        self.template_dict['cycle_dir'] = cycle_dir

        # Add the jedi interface to the dictionary
        self.jedi_interface = jedi_interface
        self.template_dict['model_component'] = jedi_interface

        # Add experiment info to dictionary
        self.template_dict['experiment_id'] = experiment_id
        self.template_dict['experiment_root'] = experiment_root

        # List of all potential valid keys that can be used in templates
        self.valid_template_keys = [
            'analysis_variables',
            'background_error_model',
            'background_frequency',
            'background_time',
            'crtm_coeff_dir',
            'ensemble_num_members',
            'gradient_norm_reduction',
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
            'minimizer',
            'gsibec_npx_proc',
            'gsibec_npy_proc',
            'npx_proc',
            'npy_proc',
            'number_of_iterations',
            'swell_static_files',
            'total_processors',
            'vertical_localization_apply_log_transform',
            'vertical_localization_function',
            'vertical_localization_ioda_vertical_coordinate',
            'vertical_localization_ioda_vertical_coordinate_group',
            'vertical_localization_lengthscale',
            'vertical_localization_method',
            'vertical_resolution',
            'window_begin',
            'window_begin_iso',
            'window_end_iso',
            'window_length',
        ]

    # ----------------------------------------------------------------------------------------------

    # Function to add key to the template dictionary
    def add_key(self, key, element):

        # First assert that key is allowed
        self.logger.assert_abort(key in self.valid_template_keys, f'Trying to add key \'{key}\' ' +
                                 f'to jedi config rendering dictionary. But the key is not part ' +
                                 f'of the valid keys: \'{self.valid_template_keys}\'')

        # Add element to dictionary
        self.template_dict[key] = element

    # ----------------------------------------------------------------------------------------------

    # Open the file at the provided path, use dictionary to complete templates and return dictionary
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

    # ----------------------------------------------------------------------------------------------

    # Prepare path to oops file and call rendering
    def render_oops_file(self, config_name):

        # Path to configuration file
        config_file = os.path.join(self.jedi_config_path, 'oops', f'{config_name}.yaml')
        print(config_file)
        # Render templates in file and return dictionary
        return self.__open_file_render_to_dict__(config_file)

    # ----------------------------------------------------------------------------------------------

    # Prepare path to interface model file and call rendering
    def render_interface_model(self, config_name):

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

    # Prepare path to interface observations file and call rendering
    def render_interface_observations(self, config_name):

        # Assert that there is a jedi interface associated with the task
        self.logger.assert_abort(self.jedi_interface is not None, f'In order to render a ' +
                                 f'jedi interface config file the task must have an associated' +
                                 f'jedi interface.')

        # Path to configuration file
        config_file = os.path.join(self.jedi_config_path, 'interfaces', self.jedi_interface,
                                   'observations', f'{config_name}.yaml')

        # Render templates in file and return dictionary
        return self.__open_file_render_to_dict__(config_file)

    # ----------------------------------------------------------------------------------------------

    # Prepare path to interface metadata file and call rendering
    def render_interface_meta(self, model_component_in=None):

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
