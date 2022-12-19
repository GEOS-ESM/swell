# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

import datetime
import isodate
import os
import yaml

from swell.utilities.jinja2 import template_string_jinja2

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

    def __init__(self, input_file, logger, **kwargs):

        # Keep track of the input config file
        self.__input_file__ = input_file

        # Keep copy of owner's logger
        self.__logger__ = logger

        # Read the configuration yaml file
        with open(self.__input_file__, 'r') as ymlfile:
            self.__config__ = yaml.safe_load(ymlfile)

        # Get model part of the config
        self.__model__ = kwargs['model']
        if self.__model__ is not None:
            # Assert the model name is found in the config
            if self.__model__ not in self.__config__['models'].keys():
                self.__logger__.abort(f'Did not find the model \'{self.__model__}\' in the ' +
                                      f'experiment configuration')
            # Extract the model specific part of the config
            model_config = self.__config__['models'][self.__model__]
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

        # Add the experiment directory to the configuration
        experiment_root = self.get('experiment_root')
        experiment_id = self.get('experiment_id')
        experiment_dir = os.path.join(experiment_root, experiment_id)
        self.__config__['experiment_dir'] = experiment_dir

        # Swell datetime format (avoid colons in paths and filenames)
        self.__datetime_swl_format__ = "%Y%m%dT%H%M%SZ"

        # ISO datetime format
        self.__datetime_iso_format__ = "%Y-%m-%dT%H:%M:%SZ"

        # If datetime passed add some extra datetime parameters to config
        if 'datetime_in' in kwargs and kwargs['datetime_in'] is not None:
            self.add_cycle_time_parameter(kwargs['datetime_in'].datetime)

            if self.get('data_assimilation_run', False):
                self.add_data_assimilation_window_parameters()

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

    def put(self, key, value):
        self.__config__[key] = value

    # ----------------------------------------------------------------------------------------------

    def use_config_to_template_string(self, string_in):

        return template_string_jinja2(self.__logger__, string_in, self.__config__)

    # ----------------------------------------------------------------------------------------------

    def get_datetime_format(self):
        return self.__datetime_swl_format__

    # ----------------------------------------------------------------------------------------------

    def add_cycle_time_parameter(self, cycle_dt):
        """
        Defines cycle time parameter and adds to config
        """

        # Add current cycle to the config
        # -------------------------------
        current_cycle = cycle_dt.strftime(self.__datetime_swl_format__)
        self.put('current_cycle', current_cycle)

        # Add cycle directory to config
        # -----------------------------
        cycle_dir = current_cycle
        if self.__model__ is not None:
            cycle_dir = cycle_dir + '-' + self.__model__
        cycle_dir = os.path.join(self.__config__['experiment_dir'], 'run', cycle_dir)

        self.put('cycle_dir', cycle_dir)

    # ----------------------------------------------------------------------------------------------

    def add_data_assimilation_window_parameters(self):
        """
        Defines cycle dependent parameters for the data assimilation window and adds to config
        """

        # Current cycle datetime object
        current_cycle_dto = datetime.datetime.strptime(self.get('current_cycle'),
                                                       self.__datetime_swl_format__)

        # Type of data assimilation window (3D or 4D)
        window_type = self.get('window_type')

        # Time from beginning of the window to the middle of the window
        window_offset = self.get('window_offset')
        window_offset_dur = isodate.parse_duration(window_offset)

        # Compute window beginning time
        window_begin_dto = current_cycle_dto - window_offset_dur

        # Background time for satbias files
        background_time_offset = self.get('background_time_offset')
        background_time_offset_dur = isodate.parse_duration(background_time_offset)

        background_time_dto = current_cycle_dto - background_time_offset_dur

        # Background time for the window
        if window_type == '4D':
            local_background_time = window_begin_dto
        elif window_type == '3D':
            local_background_time = current_cycle_dto
        else:
            self.__logger__.abort('add_data_assimilation_window_parameters: window type must be ' +
                                  'either 4D or 3D')

        window_begin = window_begin_dto.strftime(self.__datetime_swl_format__)
        window_begin_iso = window_begin_dto.strftime(self.__datetime_iso_format__)
        background_time = background_time_dto.strftime(self.__datetime_swl_format__)
        local_background_time_iso = local_background_time.strftime(self.__datetime_iso_format__)
        local_background_time = local_background_time.strftime(self.__datetime_swl_format__)

        # Create new dictionary with these items
        self.put('window_begin', window_begin)
        self.put('window_begin_iso', window_begin_iso)
        self.put('background_time', background_time)
        self.put('local_background_time', local_background_time)
        self.put('local_background_time_iso', local_background_time_iso)


# ----------------------------------------------------------------------------------------------
