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

# --------------------------------------------------------------------------------------------------


class EvaComparisonIncrement(taskBase):

    def cycles_in_experiment(self, path):
        cycle_glob = os.path.join(os.path.dirname(path), '..', 'run', '*Z', self.get_model())
        cycle_paths = glob.glob(cycle_glob)

        cycle_times = []

        for cycle_path in cycle_paths:
            cycle_time = cycle_path.split(f'Z/{self.get_model()}')[0].split('run/')[1]
            cycle_times.append(cycle_time)

        return cycle_times

    def execute(self) -> None:

        model = self.get_model()

        eva_path = os.path.join(self.experiment_path(), self.experiment_id()+'-suite', 'eva')
        eva_config_file = os.path.join(eva_path, f'comparison_increment-{model}.yaml')
        with open(eva_config_file, 'r') as eva_config_file_open:
            eva_str_template = eva_config_file_open.read()

        experiment_paths = self.config.comparison_experiment_paths()

        experiment_path_1 = experiment_paths[0]
        experiment_path_2 = experiment_paths[1]

        experiment_id_1 = os.path.basename(os.path.dirname(experiment_path_1))
        experiment_id_2 = os.path.basename(os.path.dirname(experiment_path_2))

        cycle_times_1 = self.cycles_in_experiment(experiment_path_1)
        cycle_times_2 = self.cycles_in_experiment(experiment_path_2)

        cycle_times = list(set(cycle_times_1) & set(cycle_times_2))

        for cycle_time in cycle_times:
            cycle_dir = os.path.join(self.experiment_root(), 'run', cycle_time, self.get_model(), 'eva')
            os.makedirs(cycle_dir, exist_ok=True)

            cycle_time_dto = datetime.datetime.strptime(cycle_time, '%Y%m%dT%H%M%SZ')

            # Info to task log
            info_string = 'Running Eva to plot from the increment file'
            self.logger.info('')
            self.logger.info(info_string)
            self.logger.info('-'*len(info_string))

            # Create time strings for eva_override directory
            cycle_time_reformat = cycle_time_dto.strftime('%Y%m%d_%H%M%Sz')

            # Create dictionary used to override the eva config
            eva_override = {}

            # Soca case
            if model == 'geos_marine':
                ocn_cycle_time = cycle_time_dto.strftime('%Y-%m-%dT%H:%M:%SZ')
                incr_file_1 = f'ocn.{experiment_id_1}.incr.{ocn_cycle_time}.nc'
                incr_file_2 = f'ocn.{experiment_id_2}.incr.{ocn_cycle_time}.nc'

            cycle_dir_1 = os.path.join(os.path.dirname(experiment_path_1), '..', 'run', cycle_time, self.get_model())
            cycle_dir_2 = os.path.join(os.path.dirname(experiment_path_2), '..', 'run', cycle_time, self.get_model())

            increment_file_path_1 = os.path.join(cycle_dir_1, incr_file_1)
            increment_file_path_2 = os.path.join(cycle_dir_2, incr_file_2)

            eva_override['cycle_dir'] = self.cycle_dir()
            eva_override['cycle_time'] = cycle_time_reformat
            eva_override['increment_file_path_1'] = increment_file_path_1
            eva_override['increment_file_path_2'] = increment_file_path_2

            # Override the eva dictionary
            eva_str = template_string_jinja2(self.logger, eva_str_template, eva_override)
            eva_dict = yaml.safe_load(eva_str)

            # Write eva dictionary to file
            # ----------------------------
            conf_output = os.path.join(self.cycle_dir(), 'eva', 'increment', 'comparison_increment_eva.yaml')
            os.makedirs(os.path.dirname(conf_output), exist_ok=True)
            with open(conf_output, 'w') as outfile:
                yaml.dump(eva_dict, outfile, default_flow_style=False)

            # Call eva
            # --------
            eva(eva_dict)
