# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import copy
import datetime as pydatetime
import glob
import isodate
import os
import string
import re
import yaml


# --------------------------------------------------------------------------------------------------
#  @package configuration
#
#  Class containing the configuration. This is a dictionary that is converted from
#  an input yaml configuration file. Various function are included for interacting with the
#  dictionary.
#
# --------------------------------------------------------------------------------------------------


class Config(dict):
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
       replace(s):
         Interpolates variables in string using defined parameters. This is
         the default call method (__call__).
    """

    # ----------------------------------------------------------------------------------------------

    def __init__(self, input, logger):
        """Reads YAML file(s) as a dictionary.

        Environment definitions and root-level YAML parameters are extracted to be
        used for variable interpolation within strings (see replace()).

        Parameters
        ----------
        input : string, required Name of YAML file(s)

        Returns
        -------
        config : Config, dict
          Config object
        """

        # Keep track of the input config file
        self.input = input

        # Read the configuration yaml file(s)
        with open(self.input, 'r') as ymlfile:
            config = yaml.safe_load(ymlfile)

        # Initialize the parent class with the config
        super().__init__(config)

        # Standard datetime format for config
        self.dt_format = "%Y-%m-%dT%H:%M:%SZ"

        # Create list of definitions from top level of dictionary
        self.defs = {}
        self.defs.update({k: str(v) for k, v in iter(self.items())
                         if not isinstance(v, dict) and not isinstance(v, list)})

        # Keep copy of logger
        self.logger = logger

    # ----------------------------------------------------------------------------------------------

    def merge(self, other):
        """ Merge another dictionary with self

        Parameters
        ----------
        other : dictionary, required
          other dictionary to merge
        """

        # Merge the other dictionary into self
        self.update(other)

        # Overwrite the top level definitions
        self.defs.update({k: str(v) for k, v in iter(self.items())
                         if not isinstance(v, dict) and not isinstance(v, list)})

    # ----------------------------------------------------------------------------------------------

    def add_cyle_time_parameter(self, cycle_dt):
        """ Add cyle time to the configuration

        Parameters
        ----------
        cycle_dt : datetime, required
          Current cycle date/time as datetime object
        """

        # Create new dictionary to hold cycle time
        cycle_dict = {}
        cycle_dict['current_cycle'] = cycle_dt.strftime(self.dt_format)

        # Merge with self
        self.merge(cycle_dict)

# --------------------------------------------------------------------------------------------------

    def add_data_assimilation_window_parameters(self):
        """ Defines cycle dependent parameters for the data assimilation window

        Parameters defined by this method are needed for resolving
        time-dependent variables using the replace() method.

        Parameters
        ----------
        cycle_dt : datetime, required
          Current cycle date/time as datetime object
        """

        # Current cycle datetime object
        current_cycle_dto = pydatetime.datetime.strptime(self.get('current_cycle'), self.dt_format)

        # Type of data assimilation window (3D or 4D)
        window_type = self.get('window_type', '4D')

        # Extract window information and convert to duration
        window_length = self.get('window_length', 'PT6H')
        window_offset = self.get('window_offset', 'PT3H')

        window_offset_dur = isodate.parse_duration(window_offset)

        # Compute window beginning time
        window_begin_dto = current_cycle_dto - window_offset_dur

        # Background time for satbias files
        background_time_offset = self.get('background_time_offset', 'PT9H')
        background_time_offset_dur = isodate.parse_duration(background_time_offset)

        background_time_dto = current_cycle_dto - background_time_offset_dur

        # Background time for the window
        if window_type == '4D':
            local_background_time = window_begin_dto
        elif window_type == '3D':
            local_background_time = current_cycle_dto
        else:
            self.logger.abort("add_data_assimilation_window_parameters: window type must be " +
                              "either 4D or 3D")

        # Create new dictionary with these items
        window_dict = {}
        window_dict['window_type'] = window_type
        window_dict['window_length'] = window_length
        window_dict['window_offset'] = window_offset
        window_dict['window_begin'] = window_begin_dto.strftime(self.dt_format)
        window_dict['background_time'] = background_time_dto.strftime(self.dt_format)
        window_dict['local_background_time'] = local_background_time.strftime("%Y%m%d.%H%M%S")

        # Merge with self
        self.merge(window_dict)

    # --------------------------------------------------------------------------------------------------

    def resolve_config_file(self):
        """Resolves/interpolates all defined variables in the base configuration.

        Returns
        -------
        d: dict
          YAML dictionary with all defined variables interpolated.
        """

        # Read input file as text file
        with open(self.input) as f:
            text = f.read()

        # Replace any unresolved variables in the file
        text = replace(text, **self.defs)

        # Return a yaml
        resolved_dict = yaml.safe_load(text)

        # Merge dictionary
        self.merge(resolved_dict)

    # ----------------------------------------------------------------------------------------------

    def overlay(self, hash, override=False, root=None):
        """Combines two dictionaries.

        This method recursively traverses the nodes of the dictionaries to
        locate the appropriate insertion point at the leaf-nodes.

        Parameters
        ----------
        hash : dict, required
          New dictionary to be added

        root : dict, private
          Root node to add new values. This is set during recursion.

        override : boolean, optional
          Indicates whether existing dictionary entries should be overwritten.
        """

        if root is None:
            root = self

        for key in hash:

            if key not in root:
                if isinstance(hash[key], dict):
                    root[key] = copy.deepcopy(hash[key])
                else:
                    root[key] = hash[key]
            elif isinstance(hash[key], dict) and isinstance(root[key], dict):
                self.overlay(hash[key], override, root[key])
            else:
                if override:
                    root[key] = hash[key]

    # ----------------------------------------------------------------------------------------------

    def replace(s, **defs):
        """Interpolate/replace variables in string

        Resolved variable formats are: $var, {{var}} and $(var). Undefined
        variables remain unchanged in the returned string. This method will
        recursively resolve variables of variables.

        Parameters
        ----------
        s : string, required
            Input string containing variables to be resolved.
        defs: dict, required
            dictionary of definitions for resolving variables expressed
            as key-word arguments.

        Returns
        -------
        s_interp: string
            Interpolated string. Undefined variables are left unchanged.
        """

        expr = s

        # Resolve special variables: {{var}}
        for var in re.findall(r'{{(\w+)}}', expr):
            if var in defs:
                expr = re.sub(r'{{'+var+'}}', defs[var], expr)

        # Resolve special variables: $(var)
        close = "\)"
        for var in re.findall(r'\$\((\w+)\)', expr):
            if var in defs:
                expr = re.sub(r'\$\('+var+'\)', defs[var], expr)

        # Resolve defs
        s_interp = string.Template(expr).safe_substitute(defs)

        # Recurse until no substitutions remain
        if s_interp != s:
            s_interp = replace(s_interp, **defs)

        return s_interp
