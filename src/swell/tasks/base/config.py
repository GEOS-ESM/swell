# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import yaml


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

    def __init__(self, input_file, logger, model):

        # Keep copy of owner's logger
        self.__logger__ = logger

        # Read the configuration yaml file
        with open(input_file, 'r') as ymlfile:
            self.__config__ = yaml.safe_load(ymlfile)

        # Get model part of the config
        if model is not None:
            # Assert the model name is found in the config
            if model not in self.__config__['models'].keys():
                self.__logger__.abort(f'Did not find the model \'{model}\' in the ' +
                                      f'experiment configuration')
            # Extract the model specific part of the config
            model_config = self.__config__['models'][model]
            # Add model component to config
            self.__config__['model_component'] = model
        else:
            model_config = {}

        # Remove the model specific part from the full config
        if 'models' in self.__config__.keys():
            del self.__config__['models']

        # Assert that the full and model level configs have only unique keys
        for key in self.__config__.keys():
            if key in model_config.keys():
                self.__logger__.abort(f'Model config contains the key \'{key}\'. Which is ' +
                                      f'also contained in the top level config.')

        # Now merge the top level config and the model specific parts of the config. This prevents
        # tasks from accessing the config associated with any model other than the one they are
        # supposed to act upon.
        self.__config__.update(model_config)

    # ----------------------------------------------------------------------------------------------

    def get(self, key, default='NODEFAULT'):

        if key in self.__config__.keys():
            return self.__config__[key]
        else:
            if default == 'NODEFAULT':
                self.__logger__.abort(f'In config.get the key \'{key}\' was not found in the ' +
                                      f'configuration and no default was provided.')
            else:
                return default


# ----------------------------------------------------------------------------------------------
