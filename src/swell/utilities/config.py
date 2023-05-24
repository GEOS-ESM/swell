# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import yaml

from swell.swell_path import get_swell_path


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

    def __init__(self, input_file, logger, task_name, model):

        # Keep copy of owner's logger
        self.__logger__ = logger

        # Read the configuration yaml file
        with open(input_file, 'r') as ymlfile:
            experiment_dict = yaml.safe_load(ymlfile)

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
         with open(os.path.join(get_swell_path(), 'tasks', 'questions.yaml'), 'r') as ymlfile:
            question_dict = yaml.safe_load(ymlfile)

        # Loop through the dictionary
        for experiment_key, experiment_value in experiment_dict.items():

            # Loop through the question dictionary
            for question_key, question_value in question_dict.items():

                # List of valid tasks
                if task_name in question_value['tasks']:

                    # Add this variable to the object
                    setattr(self, f'__{experiment_key}__', experiment_value)

                    # Add a method to get the variable
                    setattr(self, f'{experiment_key}', self.get(experiment_key))

    # ----------------------------------------------------------------------------------------------

    def get(self, experiment_key):
        def getter():
            try:
                var = getattr(self, f'__{experiment_key}__')
            except Exception e:
                self.logger.abort(f'In config class trying to get variable {experiment_key} but ' +
                                  f'it was not created. Ensure that the variable is in the ' +
                                  f'experiment configuration and that the task can access that ' +
                                  f'key based on the rules in tasks/questions.yaml.')
            return getattr(self, f'__{experiment_key}__')
        return getter

# ----------------------------------------------------------------------------------------------
