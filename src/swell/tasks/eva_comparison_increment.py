# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import yaml
import glob
import datetime

from eva.eva_driver import eva

from swell.tasks.base.task_base import taskBase
from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.data_assimilation_window_params import DataAssimilationWindowParams

# --------------------------------------------------------------------------------------------------


class EvaComparisonIncrement(taskBase):

    def cycles_in_experiment(self, path):
        cycle_glob = os.path.join(os.path.dirname(path), '..', 'run', '*Z', self.get_model())
        cycle_paths = glob.glob(cycle_glob)

        cycle_times = []

        for cycle_path in cycle_paths:
            cycle_time = cycle_path.split(f'/{self.get_model()}')[0].split('run/')[1]
            cycle_times.append(cycle_time)

        return cycle_times

    def execute(self) -> None:

        model = self.get_model()

        # Open the eva configuration file
        eva_path = os.path.join(self.experiment_path(), self.experiment_id()+'-suite', 'eva')
        eva_config_file = os.path.join(eva_path, f'comparison_increment-{model}.yaml')
        with open(eva_config_file, 'r') as eva_config_file_open:
            eva_str_template = eva_config_file_open.read()

        # Get the paths for the two experiments
        experiment_paths = self.config.comparison_experiment_paths()

        experiment_path_1 = experiment_paths[0]
        experiment_path_2 = experiment_paths[1]

        # Experiment IDs for the two experiments
        experiment_id_1 = os.path.basename(os.path.dirname(experiment_path_1)).replace('-suite', '')
        experiment_id_2 = os.path.basename(os.path.dirname(experiment_path_2)).replace('-suite', '')

        # Window information
        window_offset = self.config.window_offset()
        window_type = self.config.window_type()

        # Cycle times in the run directory for each experiment
        cycle_times_1 = self.cycles_in_experiment(experiment_path_1)
        cycle_times_2 = self.cycles_in_experiment(experiment_path_2)

        # Shared cycle times for each experiment
        cycle_times = list(set(cycle_times_1) & set(cycle_times_2))

        for cycle_time in cycle_times:

            # Create the cycle dir for this experiment
            cycle_dir = os.path.join(self.experiment_path(), 'run', cycle_time, self.get_model())
            os.makedirs(cycle_dir, exist_ok=True)

            cycle_time_dto = datetime.datetime.strptime(cycle_time, '%Y%m%dT%H%M%SZ')

            da_window_params = DataAssimilationWindowParams(self.logger, cycle_time_dto.strftime(
                '%Y-%m-%dT%H:%M:%SZ'))

            window_begin_dto = da_window_params.window_begin(window_offset, dto=True)
            window_begin = window_begin_dto.strftime('%Y%m%d_%H%M%Sz')

            # Info to task log
            info_string = 'Running Eva to plot from the increment file'
            self.logger.info('')
            self.logger.info(info_string)
            self.logger.info('-'*len(info_string))

            # Create time strings for eva_override directory
            cycle_time_reformat = cycle_time_dto.strftime('%Y%m%d_%H%M%Sz')

            # Define the increment filename and path
            # For 3D-Var and 3D-FGAT, the increment file is in the middle of the DA window
            # For 3D-FGAT atmos, the increment is at the beginning of the DA window. This
            # is just a limited implementation of 4DVAR in SWELL by turning the linear operator off,
            # where the cost-type is 4D-VAR in OOPS folder.
            # TODO: This really complicates the increment file naming and path for now, this
            # is a temporary solution (I'm refering to window type and atmos if statement)
            # TODO: Increment iteration number may change according to outer iteration loops
            # which is currenly manually set in varincrement1.yaml
            # For now we are only plotting the first one
            iter_no = 1
            incr_file_1 = f'{experiment_id_1}.increment-iter{iter_no}.{cycle_time_reformat}.nc4'
            incr_file_2 = f'{experiment_id_2}.increment-iter{iter_no}.{cycle_time_reformat}.nc4'

            if window_type == '4D' and 'atmos' in self.suite_name():
                incr_file_1 = f'{experiment_id_1}.increment-iter{iter_no}.{window_begin}.nc4'
                incr_file_2 = f'{experiment_id_2}.increment-iter{iter_no}.{window_begin}.nc4'

            # Create dictionary used to override the eva config
            eva_override = {}

            # Soca case
            if model == 'geos_marine':
                ocn_cycle_time = cycle_time_dto.strftime('%Y-%m-%dT%H:%M:%SZ')
                incr_file_1 = f'ocn.{experiment_id_1}.incr.{ocn_cycle_time}.nc'
                incr_file_2 = f'ocn.{experiment_id_2}.incr.{ocn_cycle_time}.nc'

            cycle_dir_1 = os.path.join(os.path.dirname(experiment_path_1), '..', 'run',
                                       cycle_time, self.get_model())
            cycle_dir_2 = os.path.join(os.path.dirname(experiment_path_2), '..', 'run',
                                       cycle_time, self.get_model())
            
            # Files to fill the template in the config file
            increment_file_path_1 = os.path.join(cycle_dir_1, incr_file_1)
            increment_file_path_2 = os.path.join(cycle_dir_2, incr_file_2)

            eva_override['cycle_dir'] = cycle_dir
            eva_override['window_begin'] = window_begin

            eva_override['cycle_dir_1'] = cycle_dir_1
            eva_override['cycle_dir_2'] = cycle_dir_2

            eva_override['cycle_time'] = cycle_time_reformat
            eva_override['increment_file_path_1'] = increment_file_path_1
            eva_override['increment_file_path_2'] = increment_file_path_2

            # Override the eva dictionary
            eva_str = template_string_jinja2(self.logger, eva_str_template, eva_override)
            eva_dict = yaml.safe_load(eva_str)

            # Write eva dictionary to file
            # ----------------------------
            conf_output = os.path.join(cycle_dir, 'eva', 'increment',
                                       'comparison_increment_eva.yaml')
            os.makedirs(os.path.dirname(conf_output), exist_ok=True)
            with open(conf_output, 'w') as outfile:
                yaml.dump(eva_dict, outfile, default_flow_style=False)

            # Call eva
            # --------
            eva(eva_dict)
