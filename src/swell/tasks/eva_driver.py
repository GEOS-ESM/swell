# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.tasks.base.task_base import taskBase
from swell.utilities.dictionary_utilities import remove_matching_keys, replace_vars_dict
from swell.utilities.observations import find_instrument_from_string, ioda_name_to_long_name
from eva.eva_base import eva


# --------------------------------------------------------------------------------------------------


class EvaDriver(taskBase):

    def execute(self):

        # Parse config for jedi_config
        # ----------------------------
        cycle_dir = self.config.get('cycle_dir')
        jedi_config_file = os.path.join(cycle_dir, 'jedi_config.yaml')
        with open(jedi_config_file, 'r') as jedi_config_string:
            config = yaml.safe_load(jedi_config_string)

        # Dictionary with observation config (from config used in JEDI)
        # -------------------------------------------------------------
        observers = config['observations']['observers']

        # Eva configuration
        # -----------------
        eva_dict_template = self.config.get('EVA')

        # Loop over observers
        # -------------------
        for observer in observers:

            # Split the full path into path and filename
            obs_path_file = observer['obs space']['obsdataout']['obsfile']
            cycle_dir, obs_file = os.path.split(obs_path_file)

            # Get instrument ioda and full name
            ioda_name = find_instrument_from_string(obs_file, self.logger)
            full_name = ioda_name_to_long_name(ioda_name, self.logger)

            # Create dictionary used to override the eva config
            eva_override = {}
            eva_override['obs_path_file'] = obs_path_file
            eva_override['instrument'] = ioda_name
            eva_override['instrument_title'] = full_name
            eva_override['simulated_variables'] = observer['obs space']['simulated variables']

            if 'channels' in observer['obs space']:
                need_channels = True
                eva_override['channels'] = observer['obs space']['channels']
            else:
                need_channels = False
                eva_override['channels'] = ''
                eva_override['channel'] = ''

            # Override the eva dictionary
            eva_dict = replace_vars_dict(eva_dict_template, **eva_override)

            # Remove channel keys if not needed
            if not need_channels:
                eva_dict = remove_matching_keys(eva_dict, 'channel', self.logger)
                eva_dict = remove_matching_keys(eva_dict, 'channels', self.logger)

            # Write eva dictionary to file
            # ----------------------------
            conf_output = os.path.join(cycle_dir, 'eva', ioda_name, ioda_name+'_eva.yaml')
            os.makedirs(os.path.dirname(conf_output), exist_ok=True)
            with open(conf_output, 'w') as outfile:
                yaml.dump(eva_dict, outfile, default_flow_style=False)

            # Call eva
            # --------
            eva(eva_dict)
