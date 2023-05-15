# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
import shutil

from jedi_bundle.bin.jedi_bundle import get_default_config, get_bundles
from swell.utilities.jinja2 import template_string_jinja2


# --------------------------------------------------------------------------------------------------


def template_dictionary_oops_config(analysis_variables, gradient_norm_reduction, minimizer,
                                    number_of_iterations, window_begin_iso, window_length):

dictionary_oops_config = {}
dictionary_oops_config['analysis_variables'] = analysis_variables
dictionary_oops_config['gradient_norm_reduction'] = gradient_norm_reduction
dictionary_oops_config['minimizer'] = minimizer
dictionary_oops_config['number_of_iterations'] = number_of_iterations
dictionary_oops_config['window_begin_iso'] = window_begin_iso
dictionary_oops_config['window_length'] = window_length
return dictionary_oops_config


# --------------------------------------------------------------------------------------------------


def template_dictionary_model_config(analysis_variables, background_frequency, cycle_dir,
                                     experiment_dir, experiment_id, horizontal_resolution,
                                     local_background_time_iso, local_background_time,
                                     npx_proc, npy_proc, swell_static_files, vertical_resolution):

dictionary_model_config = {}
dictionary_model_config['analysis_variables'] = analysis_variables
dictionary_model_config['background_frequency'] = background_frequency
dictionary_model_config['cycle_dir'] = cycle_dir
dictionary_model_config['experiment_dir'] = experiment_dir
dictionary_model_config['experiment_id'] = experiment_id
dictionary_model_config['horizontal_resolution'] = horizontal_resolution
dictionary_model_config['local_background_time_iso'] = local_background_time_iso
dictionary_model_config['local_background_time'] = local_background_time
dictionary_model_config['npx_proc'] = npx_proc
dictionary_model_config['npy_proc'] = npy_proc
dictionary_model_config['swell_static_files'] = swell_static_files
dictionary_model_config['vertical_resolution'] = vertical_resolution
return dictionary_model_config


# --------------------------------------------------------------------------------------------------


def template_dictionary_observation_config(background_time, crtm_coeff_dir, cycle_dir,
                                           experiment_id, experiment_root, model_component,
                                           window_begin):

dictionary_observation_config = {}
dictionary_observation_config['background_time'] = background_time
dictionary_observation_config['crtm_coeff_dir'] = crtm_coeff_dir
dictionary_observation_config['cycle_dir'] = cycle_dir
dictionary_observation_config['experiment_id'] = experiment_id
dictionary_observation_config['experiment_root'] = experiment_root
dictionary_observation_config['model_component'] = model_component
dictionary_observation_config['window_begin'] = window_begin
return dictionary_observation_config


# --------------------------------------------------------------------------------------------------


def __open_file_render_to_dict(logger, config_file, template_dictionary):

    # Check that config file exists
    logger.assert_abort(os.path.exists(config_file), f'In open_file_and_render failed '
                        f'to find file \'{config_file}\'')

    # Open file as a string
    with open(config_file, 'r') as config_file_open:
        config_file_str_templated = config_file_open.read()

    # Fill templates in the configuration file using the config
    config_file_str = template_string_jinja2(logger, config_file_str_templated, template_dictionary)

    # Convert string to dictionary
    return yaml.safe_load(config_file_str)


# --------------------------------------------------------------------------------------------------


def read_render_jedi_interface_oops(logger, exp_config_path, config_name,
                                     template_dictionary):

    # Path to configuration file
    config_file = os.path.join(exp_config_path, 'jedi', 'oops', f'{config_name}.yaml')

    # Render templates in file and return dictionary
    return __open_file_render_to_dict(config_file, template_dictionary)


# --------------------------------------------------------------------------------------------------


# Method to open a specific configuration file
def read_render_jedi_interface_model(logger, interface, exp_config_path, config_name,
                                     template_dictionary):

    # Path to configuration file
    config_file = os.path.join(exp_config_path, 'jedi', 'interfaces', interface, 'model',
                               f'{config_name}.yaml')

    # Render templates in file and return dictionary
    return __open_file_render_to_dict(config_file, template_dictionary)


# --------------------------------------------------------------------------------------------------


def read_render_jedi_interface_obs(logger, interface, exp_config_path, config_name,
                                   template_dictionary):

    # Path to configuration file
    config_file = os.path.join(exp_config_path, 'jedi', 'interfaces', interface, 'observations',
                               f'{config_name}.yaml')

    # Render templates in file and return dictionary
    obs_dict = __open_file_render_to_dict(config_file, template_dictionary)

    # If 4D window then add time interpolation to the dictionary
    if window_type == '4D':
        obs_dict['get values'] = {}
        obs_dict['get values']['time interpolation'] = 'linear'

    return obs_dict


# --------------------------------------------------------------------------------------------------


def read_render_jedi_interface_meta(logger, interface, exp_config_path):

    # Path to configuration file
    config_file = os.path.join(exp_config_path, 'jedi', 'interfaces', interface,
                               f'{interface}.yaml')

    # Currently no templates in these kinds of files
    template_dictionary = {}

    # Render templates in file and return dictionary
    return __open_file_render_to_dict(config_file, template_dictionary)


# --------------------------------------------------------------------------------------------------
