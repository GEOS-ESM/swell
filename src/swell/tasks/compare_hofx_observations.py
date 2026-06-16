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


class CompareIodaObservations(taskBase):

    def ioda_means(self, exp_path: str, observation: str, field: str, cutoff: int | None = None):
        ''' Reads observation files for ioda variables, returning total length of
        the array and mean of all data points.

        Arguments:
        exp_path: experiment.yaml location for experiment to compare
        observation: ioda name of observation
        field: name of data field
        cutoff: int array index to cut off mean of array

        Returns:
        Dictionary of simulated variable with length and mean
        '''

        exp_path = Path(exp_path)

        window_length = self.config.window_length()
        window_begin = self.da_window_params.window_begin(window_length)

        obs_path = (Path(os.path.dirname(exp_path)) / '..' / 'run' /
                    self.__datetime__.string_directory() / self.get_model())

        # Get list of obs files
        obs_files = list(obs_path.glob(f'*.{observation}.{window_begin}.nc4'))

        # If empty obs return black dictionary
        if len(obs_files) > 0:
            obs_file = obs_files[0]
        else:
            return {}

        # Read obs config yaml to get names of simulated variables
        yaml = YAML(typ='safe')
        with open(obs_path / 'obs.yaml', 'r') as f:
            obs_config = yaml.load(f)

        for ob in obs_config:
            if ob['observation_name'] == observation:
                simulated_variables = ob['obs space']['simulated variables']

        field_means = {}
        with Dataset(obs_file, 'r') as ds:
            for sim_var in simulated_variables:
                hofx_obs = ds[field.format(variable=sim_var)]
                field_means[sim_var] = {}
                field_means[sim_var]['length'] = len(hofx_obs)
                field_means[sim_var]['mean'] = np.mean(hofx_obs[0:cutoff])

        return field_means

    # --------------------------------------------------------------------------------------------------

    def execute(self) -> None:

        '''
        Reads observation files for hofx simulated variables, compare total length of array and mean
        of data points to evaluate diff. Output is sent to <cycle_dir>/hofx_comparison.txt
        '''

        comparison_experiment_paths = self.config.comparison_experiment_paths()
        observations = self.config.observations()
        ioda_fields = self.config.ioda_fields_for_comparison()

        experiment_tag_paths = comparison_tags(comparison_experiment_paths, self.logger)

        tag_1 = list(experiment_tag_paths.keys())[0]
        tag_2 = list(experiment_tag_paths.keys())[1]

        path_1 = list(experiment_tag_paths.values())[0]
        path_2 = list(experiment_tag_paths.values())[1]

        for observation in observations:

            output_str = f'{observation} Comparison Results\n'
            output_str += f'{tag_1}: {path_1}\n'
            output_str += f'{tag_2}: {path_2}\n'
            output_str += '\n'
            passed = True

            for field in ioda_fields:

                field_means_1 = self.ioda_means(path_1, observation, field, cutoff=int(1e4))
                field_means_2 = self.ioda_means(path_2, observation, field, cutoff=int(1e4))

                if len(field_means_1) != len(field_means_2):
                    raise Exception(f'Length of {field} fields does not '
                                    'match between experiments.')

                output_str += f'{observation}\n'
                for sim_var in field_means_1.keys():
                    len_1 = field_means_1[sim_var]['length']
                    len_2 = field_means_2[sim_var]['length']

                    mean_1 = field_means_1[sim_var]['mean']
                    mean_2 = field_means_2[sim_var]['mean']

                    output_str += f'{sim_var}\n'
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
                    output_file = Path(self.cycle_dir()) / f'ioda_{observation}_comparison.txt'

                    # Output to file
                    with open(output_file, 'w') as f:
                        f.write(output_str)
                    raise Exception(f'Mismatch in HofX observation length or average, '
                                    f'check {output_file}')

# --------------------------------------------------------------------------------------------------
