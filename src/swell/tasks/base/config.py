# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

import datetime
import isodate
import jinja2
import os
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

    def __init__(self, input_file, logger, **kwargs):
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

        # Get model part of the config
        self.__model__ = kwargs['model']
        if self.__model__ is not None:
            # Assert the model name is found in the config
            if self.__model__ not in self.__config__['models'].keys():
                self.__logger__.abort(f'Did not find the model \'{self.__model__}\' in the ' +
                                      f'experiment configuration')
            # Extract the model specific part of the config
            model_config = self.__config__['models'][self.__model__]
            # Remove the model specific part from the full config
            del self.__config__['models']
            del self.__config__['model_components']

        # Assert that the full and model level configs have only unique keys
        for key in self.__config__.keys():
            if key in model_config.keys():
                self.__logger__.abort(f'Model config contains the key \'{key}\'. Which is also ' +
                                      f'contained in the top level config.')

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
        if 'datetime_in' in kwargs:
            self.add_cycle_time_parameter(kwargs['datetime_in'].datetime)

            if self.get('data_assimilation_run', False):
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

    def put(self, key, value):
        self.__config__[key] = value

    # ----------------------------------------------------------------------------------------------

    def use_config_to_template_string(self, string_in):

        t = jinja2.Template(string_in, trim_blocks=True, lstrip_blocks=True,
                            undefined=jinja2.StrictUndefined)
        string_out = t.render(self.__config__)

        self.__logger__.assert_abort('{{' not in string_out, f'In use_config_to_template_string ' +
                                    f'the output string still contains template directives. ' +
                                    f'{string_out}')

        self.__logger__.assert_abort('}}' not in string_out, f'In use_config_to_template_string ' +
                                    f'the output string still contains template directives. ' +
                                    f'{string_out}')

        return string_out

    # ----------------------------------------------------------------------------------------------

    def get_datetime_format(self):
        return self.__datetime_swl_format__

    # ----------------------------------------------------------------------------------------------

    def add_cycle_time_parameter(self, cycle_dt):
        """ Add cycle time to the configuration

        Parameters
        ----------
        cycle_dt : datetime, required
          Current cycle date/time as datetime object
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

        # Type of data assimilation window (3D or 4D)
        window_type = self.get('window_type')

        # Extract window information and convert to duration
        window_length = self.get('window_length')
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
        self.put('window_type', window_type)
        self.put('window_length', window_length)
        self.put('window_offset', window_offset)
        self.put('window_begin', window_begin)
        self.put('window_begin_iso', window_begin_iso)
        self.put('background_time', background_time)
        self.put('local_background_time', local_background_time)
        self.put('local_background_time_iso', local_background_time_iso)


# ----------------------------------------------------------------------------------------------
