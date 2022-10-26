# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.tasks.base.task_base import taskBase
from swell.utilities.dictionary_utilities import remove_matching_keys, replace_vars_dict
from swell.utilities.observations import ioda_name_to_long_name
from eva.eva_base import eva


# --------------------------------------------------------------------------------------------------


class EvaDriver(taskBase):

    def execute(self):

        # Parse config for jedi_config
        # ----------------------------
        cycle_dir = self.config_get('cycle_dir')
        experiment_root = self.config_get('experiment_root')
        experiment_id = self.config_get('experiment_id')
        observations = self.config_get('observations')

        # Read Eva template file into dictionary
        # --------------------------------------
        exp_path = os.path.join(experiment_root, experiment_id)
        exp_suite_path = os.path.join(exp_path, experiment_id+'-suite')
        eva_config_file = os.path.join(exp_suite_path, 'eva.yaml')
        with open(eva_config_file, 'r') as eva_config_file_open:
            eva_dict_template = yaml.safe_load(eva_config_file_open)

        # Loop over observations
        # -------------------
        for observation in observations:

            # Load the observation dictionary
            observation_dict = self.open_jedi_interface_obs_config_file(observation)

            # Split the full path into path and filename
            obs_path_file = observation_dict['obs space']['obsdataout']['engine']['obsfile']
            cycle_dir, obs_file = os.path.split(obs_path_file)

            # Get instrument ioda and full name
            ioda_name = observation
            full_name = ioda_name_to_long_name(ioda_name, self.logger)

            # Log the operator being worked on
            # --------------------------------
            info_string = 'Running Eva for ' + full_name
            self.logger.info('')
            self.logger.info(info_string)
            self.logger.info('-'*len(info_string))

            # Create dictionary used to override the eva config
            eva_override = {}
            eva_override['cycle_dir'] = cycle_dir
            eva_override['obs_path_file'] = obs_path_file
            eva_override['instrument'] = ioda_name
            eva_override['instrument_title'] = full_name
            eva_override['simulated_variables'] = observation_dict['obs space']['simulated variables']

            if 'channels' in observation_dict['obs space']:
                need_channels = True
                eva_override['channels'] = observation_dict['obs space']['channels']
            else:
                need_channels = False
                eva_override['channels'] = ''
                eva_override['channel'] = ''

            # Override the eva dictionary
            eva_dict = replace_vars_dict(eva_dict_template, **eva_override)

            # Remove channel keys if not needed
            if not need_channels:
                remove_matching_keys(eva_dict, 'channel')
                remove_matching_keys(eva_dict, 'channels')

            # Write eva dictionary to file
            # ----------------------------
            conf_output = os.path.join(cycle_dir, 'eva', ioda_name, ioda_name+'_eva.yaml')
            os.makedirs(os.path.dirname(conf_output), exist_ok=True)
            with open(conf_output, 'w') as outfile:
                yaml.dump(eva_dict, outfile, default_flow_style=False)

            # Call eva
            # --------
            eva(eva_dict)
