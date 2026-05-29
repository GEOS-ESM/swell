# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from multiprocessing import Pool
import os
import yaml

from eva.eva_driver import eva

from swell.swell_path import get_swell_path
from swell.deployment.platforms.platforms import login_or_compute
from swell.tasks.base.task_base import taskBase
from swell.utilities.dictionary import remove_matching_keys, replace_string_in_dictionary
from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.observations import ioda_name_to_long_name
from swell.utilities.run_jedi_executables import check_obs
from swell.utilities.observations import ioda_name_to_long_name
from swell.utilities.comparisons import comparison_tags

# --------------------------------------------------------------------------------------------------


# Pass through to avoid confusion with optional logger argument inside eva
def run_eva(eva_dict: dict) -> eva:
    eva(eva_dict)


# --------------------------------------------------------------------------------------------------


class EvaComparisonObservations(taskBase):

    def execute(self) -> None:

        # Comparison log type
        # -------------------
        log_type = self.config.comparison_log_type()

        # Get the experiment paths
        # ------------------------
        experiment_paths = self.config.comparison_experiment_paths()

        experiment_tag_paths = comparison_tags(experiment_paths, self.logger)

        experiment_tag_1 = list(experiment_tag_paths.keys())[0]
        experiment_tag_2 = list(experiment_tag_paths.keys())[1]

        experiment_path_1 = list(experiment_tag_paths.values())[0]
        experiment_path_2 = list(experiment_tag_paths.values())[1]

        model = self.get_model()

        # Take parameters from first file
        with open(experiment_path_1, 'r') as f:
            experiment_config_1 = yaml.safe_load(f)
            experiment_id_1 = experiment_config_1['experiment_id']
            comparison_suite = experiment_config_1['suite_to_run']
            observations = experiment_config_1['models'][model]['observations']

        # Second file parameters
        with open(experiment_path_2, 'r') as f:
            experiment_config_2 = yaml.safe_load(f)
            experiment_id_2 = experiment_config_2['experiment_id']

        # JEDI config file 1
        jedi_config_file_1 = os.path.join(os.path.dirname(experiment_path_1), '..', 'run',
                                          self.__datetime__.string_directory(), model,
                                          f'jedi_{log_type}_config.yaml')

        with open(jedi_config_file_1, 'r') as f:
            jedi_config = yaml.safe_load(f)
            obs_config_1 = jedi_config['cost function']['observations']['observers']

        # JEDI config file 2
        jedi_config_file_2 = os.path.join(os.path.dirname(experiment_path_2), '..', 'run',
                                          self.__datetime__.string_directory(), model,
                                          f'jedi_{log_type}_config.yaml')

        with open(jedi_config_file_2, 'r') as f:
            jedi_config = yaml.safe_load(f)
            obs_config_2 = jedi_config['cost function']['observations']['observers']

        # Determine if running on login or compute node and set workers
        # -------------------------------------------------------------
        number_of_workers = 6
        if login_or_compute(self.platform()) == 'compute':
            number_of_workers = 40
        self.logger.info(f'Running parallel plot generation with {number_of_workers} workers')

        # Read Eva template file into dictionary
        # --------------------------------------
        # eva_path = os.path.join(self.experiment_path(), self.experiment_id()+'-suite', 'eva')
        eva_path = os.path.join(get_swell_path(), 'suites', 'compare', 'eva')
        eva_config_file = os.path.join(eva_path,
                                       f'comparison_observations-{comparison_suite}-{model}.yaml')

        with open(eva_config_file, 'r') as eva_config_file_open:
            eva_str_template = eva_config_file_open.read()

        # Set channels for which plots will be made
        # This should be configurable once we do the eva refactoring.
        # -------------------------------------------------------------
        channels_to_plot = {
            'airs_aqua': [15, 92, 128, 156, 172, 175, 190, 215, 252, 262, 310, 362, 497, 672, 914,
                          1088, 1329, 1449, 1766, 1800, 1869, 1918],
            'cris-fsr_n20': [59, 69, 82, 86, 92, 102, 107, 114, 130, 141, 153, 158, 164, 167, 168,
                             402, 487, 501, 626, 874, 882, 1008],
            'cris-fsr_npp': [59, 69, 82, 86, 92, 102, 107, 114, 130, 141, 153, 158, 164, 167, 168,
                             402, 487, 501, 626, 874, 882, 1008],
            'iasi_metop-b': [55, 70, 106, 122, 144, 176, 185, 210, 236, 254, 299, 345, 375, 404,
                             445, 552, 573, 906, 1121, 1194, 1427, 1585],
            'iasi_metop-c': [55, 70, 106, 122, 144, 176, 185, 210, 236, 254, 299, 345, 375, 404,
                             445, 552, 573, 906, 1121, 1194, 1427, 1585],
            }

        observation = self.get_parameter()

        # Set the observing system records path
        self.jedi_rendering.set_obs_records_path(self.config.observing_system_records_path(None))

        if self.get_model() == 'geos_atmosphere':
            obs_long_name = ioda_name_to_long_name(observation, self.logger)
        else:
            obs_long_name = observation

        observation_dict_1 = None
        for value in obs_config_1:
            if value['obs space']['name'] == obs_long_name:
                observation_dict_1 = value.copy()

        observation_dict_2 = None
        for value in obs_config_2:
            if value['obs space']['name'] == obs_long_name:
                observation_dict_2 = value.copy()

        if observation_dict_1 is None or observation_dict_2 is None:
            return

        # Check if IODA observation input and output have non-zero location dimensions
        use_obs_1 = check_obs(self.jedi_rendering.observing_system_records_path, observation,
                                observation_dict_1, self.cycle_time_dto(), input_and_output=True)

        use_obs_2 = check_obs(self.jedi_rendering.observing_system_records_path, observation,
                                observation_dict_2, self.cycle_time_dto(), input_and_output=True)

        use_obs = use_obs_1 and use_obs_2

        if not use_obs:
            return

        # Split the full path into path and filename
        obs_path_file_1 = observation_dict_1['obs space']['obsdataout']['engine']['obsfile']
        cycle_dir_1, obs_file_1 = os.path.split(obs_path_file_1)

        # Split the full path into path and filename
        obs_path_file_2 = observation_dict_2['obs space']['obsdataout']['engine']['obsfile']
        cycle_dir_2, obs_file_2 = os.path.split(obs_path_file_2)

        # Check for need to add 0000 to the file
        # --------------------------------------
        if not os.path.exists(obs_path_file_1):
            obs_path_file_name, obs_path_file_ext = os.path.splitext(obs_path_file_1)
            obs_path_file_0000 = obs_path_file_name + '_0000' + obs_path_file_ext
            if not os.path.exists(obs_path_file_0000):
                self.logger.abort(f'No observation file found for {obs_path_file_1} or ' +
                                    f'{obs_path_file_0000}')
            obs_path_file_1 = obs_path_file_0000

        # Check for need to add 0000 to the file
        # --------------------------------------
        if not os.path.exists(obs_path_file_2):
            obs_path_file_name, obs_path_file_ext = os.path.splitext(obs_path_file_2)
            obs_path_file_0000 = obs_path_file_name + '_0000' + obs_path_file_ext
            if not os.path.exists(obs_path_file_0000):
                self.logger.abort(f'No observation file found for {obs_path_file_2} or ' +
                                    f'{obs_path_file_0000}')
            obs_path_file_2 = obs_path_file_0000

        # Get instrument ioda and full name
        # ---------------------------------
        ioda_name = observation
        full_name = ioda_name_to_long_name(ioda_name, self.logger)

        # Create dictionary used to override the eva config
        # -------------------------------------------------
        eva_override = {}
        eva_override['cycle_dir'] = self.cycle_dir()
        eva_override['obs_path_file_1'] = obs_path_file_1
        eva_override['obs_path_file_2'] = obs_path_file_2
        eva_override['instrument'] = ioda_name
        eva_override['instrument_title'] = full_name
        eva_override['simulated_variables'] = \
            observation_dict_1['obs space']['simulated variables']
        eva_override['map_projection'] = 'plcarr'
        eva_override['domain'] = 'global'
        eva_override['experiment_id_1'] = experiment_id_1
        eva_override['experiment_id_2'] = experiment_id_2

        eva_override['experiment_tag_1'] = experiment_tag_1
        eva_override['experiment_tag_2'] = experiment_tag_2

        # If filename contains icec_ change map projection to polar stereographic
        # -----------------------------------------------------------------------
        if 'icec_' in obs_file_1:
            eva_override['map_projection'] = 'npstere'
            eva_override['domain'] = 'north'

            # if file name has 'south" or "sh" then change to south polar stereographic
            # ---------------------------------------------------------------
            if 'south' in obs_file_1 or 'sh' in obs_file_1:
                eva_override['map_projection'] = 'spstere'
                eva_override['domain'] = 'south'

        # # Check if the "passivate" condition exists within the "obs filters" list
        passivate_exists = any(
            filter_item.get('action', {}).get('name') == 'passivate'
            for filter_item in observation_dict_1.get('obs filters', [])
        )

        if passivate_exists:
            self.logger.info("Condition 'passivate' exists in 'obs filters'")
            eva_override['passivated_variables'] = True

        if 'channels' in observation_dict_1['obs space']:
            need_channels = True
            if observation in channels_to_plot:
                eva_override['channels'] = channels_to_plot[observation]
            else:
                eva_override['channels'] = observation_dict_1['obs space']['channels']
        else:
            need_channels = False
            eva_override['channels'] = ''
            eva_override['channel'] = ''

        # Override the eva dictionary
        # ---------------------------
        eva_str = template_string_jinja2(self.logger, eva_str_template, eva_override)
        eva_dict = yaml.safe_load(eva_str)

        # Remove channel keys if not needed
        # ---------------------------------
        if not need_channels:
            remove_matching_keys(eva_dict, 'channel')
            remove_matching_keys(eva_dict, 'channels')
            eva_dict = replace_string_in_dictionary(eva_dict, '${channel}', '')

        # Write eva dictionary to file
        # ----------------------------
        conf_output = os.path.join(self.cycle_dir(), 'eva', ioda_name, ioda_name+'_eva.yaml')
        os.makedirs(os.path.dirname(conf_output), exist_ok=True)
        with open(conf_output, 'w') as outfile:
            yaml.dump(eva_dict, outfile, default_flow_style=False)

        # Call Eva
        # --------
        run_eva(eva_dict)
