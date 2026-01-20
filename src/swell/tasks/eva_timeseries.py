# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from multiprocessing import Pool
from datetime import datetime as dt
import isodate
import os
import yaml

from swell.deployment.platforms.platforms import login_or_compute
from swell.tasks.base.task_base import taskBase
from swell.tasks.base.task_setup import TaskSetup
from swell.tasks.base.task_attributes import task_attributes
from swell.utilities.question_defaults import QuestionDefaults as qd
from swell.utilities.datetime_util import datetime_formats
from swell.utilities.dictionary import remove_matching_keys, replace_string_in_dictionary
from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.observations import ioda_name_to_long_name

# --------------------------------------------------------------------------------------------------


# Pass through to avoid confusion with optional logger argument inside eva
def run_eva(eva_dict: dict):

    from eva.eva_driver import eva
    eva(eva_dict)


# --------------------------------------------------------------------------------------------------

task_name = 'EvaTimeseries'


@task_attributes.register(task_name)
class Setup(TaskSetup):
    def set_attributes(self):
        self.base_name = task_name
        self.time_limit = True
        self.is_cycling = True
        self.is_model = True
        self.slurm = {}
        self.questions = [
            qd.background_time_offset(),
            qd.crtm_coeff_dir(),
            qd.observations(),
            qd.observing_system_records_path(),
            qd.window_length(),
            qd.ncdiag_experiments(),
            qd.marine_models(),
        ]

# --------------------------------------------------------------------------------------------------


class EvaTimeseries(taskBase):

    def execute(self) -> None:

        window_length = self.config.window_length()

        # Compute window beginning time
        # -----------------------------
        window_begin = self.da_window_params.window_begin(window_length)
        background_time = self.da_window_params.background_time(
                self.config.background_time_offset())

        ncdiag_experiments = self.config.ncdiag_experiments()

        # Use built-in methods to get the start and end cycle points
        # ----------------------------------------------------------
        start_cycle_point_dto = self.start_cycle_point_dto()
        final_cycle_point_dto = self.final_cycle_point_dto()

        # Parse window length and offset
        window_duration = isodate.parse_duration(window_length)
        window_offset = self.da_window_params.window_offset(window_length, dto=True)

        # Create a list of cycles beginning with the start cycle point
        # and ending with the final cycle point using the window length
        # -------------------------------------------------------------
        ncdiag_cycles = []

        current_time = start_cycle_point_dto
        while current_time <= final_cycle_point_dto:
            ncdiag_cycles.append(current_time)
            current_time += window_duration

        # Create JEDI interface config templates dictionary
        # -------------------------------------------------
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', self.config.crtm_coeff_dir(None))
        self.jedi_rendering.add_key('window_begin', window_begin)
        self.jedi_rendering.add_key('window_length', window_length)

        # Get the model
        # -------------
        model = self.get_model()
        self.jedi_rendering.add_key('marine_models', self.config.marine_models(None))

        # Determine if running on login or compute node and set workers
        # -------------------------------------------------------------
        number_of_workers = 6
        if login_or_compute(self.platform()) == 'compute':
            number_of_workers = 40
        self.logger.info(f'Running parallel plot generation with {number_of_workers} workers')

        # Read Eva template file into dictionary
        # --------------------------------------
        eva_path = os.path.join(self.experiment_path(), self.experiment_id()+'-suite', 'eva')
        eva_config_file = os.path.join(eva_path, f'timeseries-{model}.yaml')
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

        # Loop over observations and create dictionaries
        # ----------------------------------------------
        eva_dicts = []  # Empty list of dictionaries

        # Set the observing system records path
        self.jedi_rendering.set_obs_records_path(self.config.observing_system_records_path(None))

        for observation in self.config.observations():

            # Load the observation dictionary
            observation_dict = self.jedi_rendering.render_interface_observations(observation)

            obs_filenames = []
            # Split the full path into path and filename
            obs_path_file = observation_dict['obs space']['obsdataout']['engine']['obsfile']
            cycle_dir, obs_root = os.path.split(obs_path_file)

            for ncdiag_cycle in ncdiag_cycles:

                # Obs time starts at the beginning of the cycle
                obs_time = ncdiag_cycle - window_offset
                obs_root = '.'.join([ncdiag_experiments[0],
                                     observation,
                                    dt.strftime(obs_time,
                                                datetime_formats['directory_format']),
                                     'nc4'])

                obs_file = os.path.join(self.experiment_path(),
                                        'run',
                                        dt.strftime(ncdiag_cycle,
                                                    datetime_formats['directory_format']),
                                        self.get_model(),
                                        obs_root)
                obs_filenames.append(obs_file)

            # Get instrument ioda and full name
            # ---------------------------------
            ioda_name = observation
            full_name = ioda_name_to_long_name(ioda_name, self.logger)

            # Create dictionary used to override the eva config
            # -------------------------------------------------
            eva_override = {}
            eva_override['cycle_dir'] = self.cycle_dir()
            eva_override['obs_filenames'] = obs_filenames
            eva_override['instrument'] = ioda_name
            eva_override['instrument_title'] = full_name
            eva_override['simulated_variables'] = \
                observation_dict['obs space']['simulated variables']
            eva_override['window_length'] = window_length
            eva_override['map_projection'] = 'plcarr'
            eva_override['domain'] = 'global'
            eva_override['start_cycle_point'] = start_cycle_point_dto.strftime('%Y-%m-%dT%H:%M:%S')
            eva_override['final_cycle_point'] = final_cycle_point_dto.strftime('%Y-%m-%dT%H:%M:%S')

            # Handle the channels key
            # -----------------------
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
                yaml.dump(eva_dict, outfile, default_flow_style=False, sort_keys=False)

            # Add eva dictionary to list
            # --------------------------
            eva_dicts.append(eva_dict)

        # Call eva in parallel
        # --------------------
        with Pool(processes=number_of_workers) as pool:
            pool.map(run_eva, eva_dicts)
