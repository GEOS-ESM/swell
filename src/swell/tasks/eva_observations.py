# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from multiprocessing import Pool
import netCDF4 as nc
import os
import yaml

from eva.eva_driver import eva

from swell.deployment.platforms.platforms import login_or_compute
from swell.tasks.base.task_base import taskBase
from swell.utilities.dictionary import remove_matching_keys, replace_string_in_dictionary
from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.observations import ioda_name_to_long_name


# --------------------------------------------------------------------------------------------------


# Pass through to avoid confusion with optional logger argument inside eva
def run_eva(eva_dict):
    eva(eva_dict)


# --------------------------------------------------------------------------------------------------


class EvaObservations(taskBase):

    def execute(self):

        # Compute window beginning time
        window_begin = self.da_window_params.window_begin(self.config.window_offset())
        background_time = self.da_window_params.background_time(self.config.window_offset(),
                                                                self.config.background_time_offset()
                                                                )

        # Create JEDI interface config templates dictionary
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', self.config.crtm_coeff_dir(None))
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Get the model
        # -------------
        model = self.get_model()

        # Determine if running on login or compute node and set workers
        # -------------------------------------------------------------
        number_of_workers = 6
        if login_or_compute(self.platform()) == 'compute':
            number_of_workers = 40
        self.logger.info(f'Running parallel plot generation with {number_of_workers} workers')

        # Read Eva template file into dictionary
        # --------------------------------------
        eva_path = os.path.join(self.experiment_path(), self.experiment_id()+'-suite', 'eva')
        eva_config_file = os.path.join(eva_path, f'observations-{model}.yaml')
        with open(eva_config_file, 'r') as eva_config_file_open:
            eva_str_template = eva_config_file_open.read()

        # Set channels for which plots will be made
        # This should be configurable once we do the eva refactoring.
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

        # Loop over observations
        # -------------------
        eva_dicts = []  # Empty list of dictionaries
        observing_system_records_path = self.config.observing_system_records_path()
        cycle_dir = self.cycle_dir()
        if observing_system_records_path == 'None':
            observing_system_records_path = os.path.join(cycle_dir, 'observing_system_records')
        cycle_time = os.path.normpath(cycle_dir).split('/')[-2]

        for observation in self.config.observations():

            # Load the observation dictionary
            observation_dict = self.jedi_rendering.render_interface_observations(
                observation,
                observing_system_records_path,
                cycle_time
            )

            # Split the full path into path and filename
            obs_path_file = observation_dict['obs space']['obsdataout']['engine']['obsfile']

            # Prevent Eva from failing if there are observation files with 0 observations
            with nc.Dataset(obs_path_file, 'r') as ds:
                loc_size = len(ds.dimensions['Location'])

            if (loc_size) < 1:
                self.logger.info(f'No observations were found for {obs_path_file}. ' +
                                 'No plots will be produced')
                continue

            cycle_dir, obs_file = os.path.split(obs_path_file)

            # Check for need to add 0000 to the file
            if not os.path.exists(obs_path_file):
                obs_path_file_name, obs_path_file_ext = os.path.splitext(obs_path_file)
                obs_path_file_0000 = obs_path_file_name + '_0000' + obs_path_file_ext
                if not os.path.exists(obs_path_file_0000):
                    self.logger.abort(f'No observation file found for {obs_path_file} or ' +
                                      f'{obs_path_file_0000}')
                obs_path_file = obs_path_file_0000

            # Get instrument ioda and full name
            ioda_name = observation
            full_name = ioda_name_to_long_name(ioda_name, self.logger)

            # Create dictionary used to override the eva config
            eva_override = {}
            eva_override['cycle_dir'] = self.cycle_dir()
            eva_override['obs_path_file'] = obs_path_file
            eva_override['instrument'] = ioda_name
            eva_override['instrument_title'] = full_name
            eva_override['simulated_variables'] = \
                observation_dict['obs space']['simulated variables']

            if 'channels' in observation_dict['obs space']:
                need_channels = True
                if observation in channels_to_plot:
                    eva_override['channels'] = channels_to_plot[observation]
                else:
                    eva_override['channels'] = observation_dict['obs space']['channels']
            else:
                need_channels = False
                eva_override['channels'] = ''
                eva_override['channel'] = ''

            # Override the eva dictionary
            eva_str = template_string_jinja2(self.logger, eva_str_template, eva_override)
            eva_dict = yaml.safe_load(eva_str)

            # Remove channel keys if not needed
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

            # Add eva dictionary to list
            # --------------------------
            eva_dicts.append(eva_dict)

        # Call eva in parallel
        # --------------------
        with Pool(processes=number_of_workers) as pool:
            pool.map(run_eva, eva_dicts)
