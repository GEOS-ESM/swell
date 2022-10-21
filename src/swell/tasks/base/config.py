# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import copy
import datetime
import glob
import isodate
import os
import string
import re
import json
import yaml

from swell.utilities.string_utils import replace_vars

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

    def __init__(self, input_file, logger, datetime_in=None):
        """Reads YAML file(s) as a dictionary.

        Environment definitions and root-level YAML parameters are extracted to be
        used for variable interpolation within strings (see replace_vars()).

        Parameters
        ----------
        input_file : string, required Name of YAML file(s)

        Returns
        -------
        config : Config, dict
          Config object
        """

        # Keep track of the input config file
        self.__input_file__ = input_file

        # Keep copy of owner's logger
        self.__logger__ = logger

        # Read the configuration yaml file
        with open(self.__input_file__, 'r') as ymlfile:
            self.__config__ = yaml.safe_load(ymlfile)

        # Swell datetime format (avoid colons in paths and filenames)
        self.__datetime_swl_format__ = "%Y%m%dT%H%M%SZ"

        # ISO datetime format
        self.__datetime_iso_format__ = "%Y-%m-%dT%H:%M:%SZ"

        # If datetime passed add some extra datetime parameters to config
        if datetime_in is not None:
            self.add_cycle_time_parameter(datetime_in.datetime)

            if self.get('data_assimilation_run', False):
                print('here')
                self.add_data_assimilation_window_parameters()

        # Create list of definitions from top level of dictionary
        #self.__defs__ = {}
        #self.__defs__.update({k: str(v) for k, v in iter(self.items())
        #                     if not isinstance(v, dict) and not isinstance(v, list)})


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

    def get_model(self, key, model, default='NODEFAULT'):

        if key in self.__config__['models'][model].keys():
            return self.__config__['models'][model][key]
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

    def put_model(self, key, value, model):
        self.__config__['models'][model][key] = value

    # ----------------------------------------------------------------------------------------------

    def merge(self, other):
        """ Merge another dictionary with self

        Parameters
        ----------
        other : dictionary, required
          other dictionary to merge
        """

        # Merge the other dictionary into self
        self.__config__.update(other)

        # Overwrite the top level definitions
        #self.__defs__.update({k: str(v) for k, v in iter(self.items())
        #                     if not isinstance(v, dict) and not isinstance(v, list)})

    # ----------------------------------------------------------------------------------------------

    def add_cycle_time_parameter(self, cycle_dt):
        """ Add cycle time to the configuration

        Parameters
        ----------
        cycle_dt : datetime, required
          Current cycle date/time as datetime object
        """

        # Add cycle time to dictionary
        self.put('current_cycle', cycle_dt.strftime(self.__datetime_swl_format__))

# --------------------------------------------------------------------------------------------------

    def add_data_assimilation_window_parameters(self):
        """ Defines cycle dependent parameters for the data assimilation window

        Parameters defined by this method are needed for resolving
        time-dependent variables using the replace_vars() method.

        Parameters
        ----------
        cycle_dt : datetime, required
          Current cycle date/time as datetime object
        """

        # Current cycle datetime object
        current_cycle_dto = datetime.datetime.strptime(self.get('current_cycle'),
                                                       self.__datetime_swl_format__)

        # Loop over models
        model_components = self.get('model_components')

        for model_component in model_components:

            # Type of data assimilation window (3D or 4D)
            window_type = self.get_model('window_type', model_component)

            # Extract window information and convert to duration
            window_length = self.get_model('window_length', model_component)
            window_offset = self.get_model('window_offset', model_component)

            window_offset_dur = isodate.parse_duration(window_offset)

            # Compute window beginning time
            window_begin_dto = current_cycle_dto - window_offset_dur

            # Background time for satbias files
            background_time_offset = self.get_model('background_time_offset', model_component)
            background_time_offset_dur = isodate.parse_duration(background_time_offset)

            background_time_dto = current_cycle_dto - background_time_offset_dur

            # Background time for the window
            if window_type == '4D':
                local_background_time = window_begin_dto
            elif window_type == '3D':
                local_background_time = current_cycle_dto
            else:
                self.__logger__.abort("add_data_assimilation_window_parameters: window type must be " +
                                      "either 4D or 3D")

            window_begin = window_begin_dto.strftime(self.__datetime_swl_format__)
            window_begin_iso = window_begin_dto.strftime(self.__datetime_iso_format__)
            background_time = background_time_dto.strftime(self.__datetime_swl_format__)
            local_background_time_iso = local_background_time.strftime(self.__datetime_iso_format__)
            local_background_time = local_background_time.strftime(self.__datetime_swl_format__)

            # Create new dictionary with these items
            self.put_model('window_type', window_type, model_component)
            self.put_model('window_length', window_length, model_component)
            self.put_model('window_offset', window_offset, model_component)
            self.put_model('window_begin', window_begin, model_component)
            self.put_model('window_begin_iso', window_begin_iso, model_component)
            self.put_model('background_time', background_time, model_component)
            self.put_model('local_background_time', local_background_time, model_component)
            self.put_model('local_background_time_iso', local_background_time_iso, model_component)

    # --------------------------------------------------------------------------------------------------

    def resolve_config_file(self):
        """Resolves/interpolates all defined variables in the base configuration.

        Returns
        -------
        d: dict
          YAML dictionary with all defined variables interpolated.
        """

        # Read input file as text file
        with open(self.__input_file__) as f:
            text = f.read()

        # Replace any unresolved variables in the file
        text = replace_vars(text, **self.__defs__)

        # Return a yaml
        resolved_dict = yaml.safe_load(text)

        # Merge dictionary
        self.merge(resolved_dict)

# ----------------------------------------------------------------------------------------------
