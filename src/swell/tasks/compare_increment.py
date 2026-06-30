# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import numpy as np
from ruamel.yaml import YAML
from netCDF4 import Dataset
from pathlib import Path
from swell.tasks.base.task_base import taskBase
from swell.utilities.comparisons import comparison_tags

# --------------------------------------------------------------------------------------------------

variables = {}

variables['geos_marine'] = ['Temp', 'Salt', 'ave_ssh']
variables['geos_atmosphere'] = ['ps', 'ts', 'ua', 'va', 't', 'q']

class CompareIncrement(taskBase):

    def var_mean(self, incr_file: str, vars: list[str], cutoff: int | None = None) -> dict:

        var_means = {}

        with Dataset(incr_file, 'r') as ds:
            for var in vars:
                ds_var = ds[var]
                var_means[var] = {}
                var_means[var]['length'] = len(ds_var)
                var_means[var]['mean'] = np.mean(ds_var[:cutoff])

        return var_means


    def execute(self) -> None:

        comparison_experiment_paths = self.config.comparison_experiment_paths()

        experiment_tag_paths = comparison_tags(comparison_experiment_paths, self.logger)

        tag_1 = list(experiment_tag_paths.keys())[0]
        tag_2 = list(experiment_tag_paths.keys())[1]

        path_1 = list(experiment_tag_paths.values())[0]
        path_2 = list(experiment_tag_paths.values())[1]

        yaml = YAML()

        increment_files = []

        for experiment_yaml in comparison_experiment_paths:

            with open(experiment_yaml, 'r') as f:
                experiment_dict = yaml.load(f)

                window_length = experiment_dict['window_length']
                window_type = experiment_dict['window_type']
        
            window_begin_dto = self.da_window_params.window_begin(window_length, dto=True)
            window_begin = window_begin_dto.strftime('%Y%m%d_%H%M%Sz')

            cycle_time_reformat = self.cycle_time_dto().strftime('%Y%m%d_%H%M%Sz')

            local_bkg_dir, local_bkg_dto = self.da_window_params.local_background_time(
                self.config.window_length(), self.config.window_type(), dto=True)
            local_bkg_time = local_bkg_dto.strftime('%Y%m%d_%H%M%Sz')

            iter_no = 1
            incr_file = f'{self.experiment_id()}.increment-iter{iter_no}.{cycle_time_reformat}.nc4'
            if self.suite_name() == 'localensembleda':
                incr_file = f'geos.mean-inc.{local_bkg_time}.nc4'
            if window_type == '4D' and 'atmos' in self.suite_name():
                incr_file = f'{self.experiment_id()}.increment-iter{iter_no}.{window_begin}.nc4'

            # Soca case
            if self.get_model() == 'geos_marine':
                ocn_cycle_time = self.cycle_time_dto().strftime('%Y-%m-%dT%H:%M:%SZ')
                incr_file = f'ocn.{self.experiment_id()}.incr.{ocn_cycle_time}.nc'

            increment_file_path = os.path.join(self.cycle_dir(), incr_file)

            increment_files.append(increment_file_path)

        var_means_1 = self.var_mean(increment_files[0])
        var_means_2 = self.var_mean(increment_files[1])

        output_str = ''
        passed = True

        for var in variables:

            output_str += f'{var} Comparison Results\n'
            output_str += f'{tag_1}: {path_1}\n'
            output_str += f'{tag_2}: {path_2}\n'
            output_str += '\n'

            len_1 = var_means_1[var]['length']
            len_2 = var_means_2[var]['length']

            mean_1 = var_means_1[var]['mean']
            mean_2 = var_means_2[var]['mean']

            output_str += f'{var}\n'
            if len_1 != len_2 or mean_1 != mean_2:
                tag_length = max(len(tag_1), len(tag_2)) + 2
                len_length = max(len(str(len_1)), len(str(len_2))) + 2
                mean_length = max(len(str(mean_1)), len(str(mean_2))) + 2
                output_str += (f'{"":<{tag_length}} {"Length":<{len_length}} '
                                f'{"Mean":<{mean_length}}\n')
                output_str += (f'{tag_1:<{tag_length}} {len_1:<{len_length}} '
                                f'{mean_1:<{mean_length}}\n')
                output_str += (f'{tag_2:<{tag_length}} {len_2:<{len_length}} '
                                f'{mean_2:<{mean_length}}\n\n')
                passed = False
            else:
                output_str += f'Passed\n\n'

        # Fail suite if not passed
        if not passed:
            output_file = Path(self.cycle_dir()) / f'increment_comparison.txt'

            # Output to file
            with open(output_file, 'w') as f:
                f.write(output_str)
            raise Exception(f'Mismatch in increment field length or average, '
                            f'check {output_file}')

# --------------------------------------------------------------------------------------------------
