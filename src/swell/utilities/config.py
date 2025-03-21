# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
import yaml
from typing import Callable

from swell.swell_path import get_swell_path
from swell.utilities.logger import Logger


# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


class Config():
    """Provides methods for reading YAML files and managing configuration
       parameters.

       Attributes
       ----------
       self : dict
         YAML definitions
       defs : dict
         Root-level YAML, environment and cycle dependent parameters

       Methods
       -------
       __init__(inputs):
         Reads in YAML files.
       define(cycle_dt):
         Defines cycle/time dependent parameters.
    """

    # ----------------------------------------------------------------------------------------------

    def __init__(self, input_file: str, logger: Logger, task_name: str, model: str) -> None:

        # Keep copy of owner's logger
        self.__logger__ = logger

        # Read the configuration yaml file
        with open(input_file, 'r') as ymlfile:
            experiment_dict = yaml.safe_load(ymlfile)

        # Save some things that all tasks can use (suite level questions)
        self.__experiment_root__ = experiment_dict.get('experiment_root')
        self.__experiment_id__ = experiment_dict.get('experiment_id')
        self.__platform__ = experiment_dict.get('platform')
        self.__start_cycle_point__ = experiment_dict.get('start_cycle_point')
        self.__suite_to_run__ = experiment_dict.get('suite_to_run')

        # If experiment_dict contains models key add the model components to the object
        if 'models' in experiment_dict.keys():
            self.__model_components__ = list(experiment_dict['models'].keys())
        else:
            self.__model_components__ = None

        # Step1: flatten the dictionary based on the model
        # ------------------------------------------------

        # Extract the model config
        if model is not None:
            # Assert the model name is found in the config
            if model not in experiment_dict['models'].keys():
                self.__logger__.abort(f'Did not find the model \'{model}\' in the ' +
                                      f'experiment configuration')
            # Extract the model specific part of the config
            model_config = experiment_dict['models'][model]
            # Add model component to config
            experiment_dict['model_component'] = model
        else:
            model_config = {}

        # Remove the model specific part from the full config
        if 'models' in experiment_dict.keys():
            del experiment_dict['models']

        # Assert that the full and model level configs have only unique keys
        for key in experiment_dict.keys():
            if key in model_config.keys():
                self.__logger__.abort(f'Model config contains the key \'{key}\'. Which is ' +
                                      f'also contained in the top level config.')

        # Now merge the top level config and the model specific parts of the config. This prevents
        # tasks from accessing the config associated with any model other than the one they are
        # supposed to act upon.
        experiment_dict.update(model_config)

        # Step 2: create variables in the object with the keys/values in the config
        # -------------------------------------------------------------------------

        # Open the question dictionary
        with open(os.path.join(get_swell_path(), 'tasks', 'task_questions.yaml'), 'r') as ymlfile:
            question_dict = yaml.safe_load(ymlfile)

        # Loop through the dictionary
        for experiment_key, experiment_value in experiment_dict.items():

            key_question_dict = question_dict.get(experiment_key)

            if key_question_dict is not None:

                if task_name in key_question_dict['tasks']:

                    # Add this variable to the object
                    setattr(self, f'__{experiment_key}__', experiment_value)

                    # Add a method to get the variable
                    setattr(self, f'{experiment_key}', self.get(experiment_key))

    # ----------------------------------------------------------------------------------------------

    def get(self, experiment_key: str) -> Callable:
        def getter(default='None'):
            return getattr(self, f'__{experiment_key}__')
        return getter

    # ----------------------------------------------------------------------------------------------

    # Implementation of __getattr__ to ensure there is no crash when a task requests a variable that
    # does not exist. This is valid so long as the task provides a default value.
    def __getattr__(self, name: str) -> Callable:
        def variable_not_found(default='LrZRExPGcQ'):
            if default == 'LrZRExPGcQ':
                self.__logger__.abort(f'In config class, trying to get variable \'{name}\' but ' +
                                      f'this variable was not created. Ensure that the variable ' +
                                      f'is in the experiment configuration and that the task can ' +
                                      f'access that key based on the rules in '
                                      f'tasks/task_questions.yaml.')
            else:
                return default
        return variable_not_found

# ----------------------------------------------------------------------------------------------
