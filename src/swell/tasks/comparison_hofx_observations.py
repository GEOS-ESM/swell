# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import numpy as np
from netCDF4 import Dataset
from pathlib import Path
from swell.tasks.base.task_base import taskBase
from swell.utilities.comparisons import comparison_tags

# --------------------------------------------------------------------------------------------------

class CompareHofxObservations(taskBase):

    def hofx_mean(self, exp_path: str, observation: str, mean_length: int = 1e4):
        exp_path = Path(exp_path)

        window_length = self.config.window_length()
        window_begin = self.da_window_params.window_begin(window_length)

        obs_file = (exp_path / '..' / 'run' / self.__datetime__.string_directory() / 
                    self.get_model() / f'*.{observation}.{window_begin}.nc4')
        
        with Dataset(obs_file, 'r') as ds:
            hofx_obs = ds['hofx'][observation]

            location_length = len(hofx_obs)
            hofx_mean = np.mean(hofx_obs[:mean_length])

        return location_length, hofx_mean
        

    def execute(self) -> None:

        comparison_experiment_paths = self.config.comparison_experiment_paths()

        experiment_tag_paths = comparison_tags(comparison_experiment_paths, self.logger)

        tag_1 = list(experiment_tag_paths.values())[0]
        tag_2 = list(experiment_tag_paths.values())[1]

        path_1 = list(experiment_tag_paths.values())[0]
        path_2 = list(experiment_tag_paths.values())[1]

        output_str = 'HofX Comparison Results\n'
        output_str += '{tag_1}: {path_1}\n'
        output_str += '{tag_2}: {path_2}\n'
        output_str += '\n'
        passed = True

        for observation in self.config.observations():
            len_1, mean_1 = self.hofx_mean(path_1, observation)
            len_2, mean_2 = self.hofx_mean(path_2, observation)

            if len_1 != len_2 or mean_1 != mean_2:
                output_str += 'Observation\n'
                output_str += f'     Length  Mean HofX\n'
                output_str += f'{tag_1}: {len_1} {mean_1:.02f}\n'
                output_str += f'{tag_2}: {len_2} {mean_2:.02f}\n\n'
                passed = False
            else:
                output_str += f'Passed\n'


        with open(Path(self.cycle_dir()) / 'hofx_comparison.txt', 'w') as f:
            f.write(output_str)

        if not passed:
            raise Exception(f'Mismatch in HofX observation length or average')

# --------------------------------------------------------------------------------------------------