# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import re
import subprocess
import numpy as np

from swell.tasks.base.task_base import taskBase

# --------------------------------------------------------------------------------------------------

class TierTestOutput(taskBase):

    def execute(self):

        all_results = {}

        experiment_paths = self.config.comparison_experiment_paths()

        for i, experiment_path in enumerate(experiment_paths):
            experiment_results = {}

            cycles_path = os.path.join(os.path.basename(experiment_path), '..', 'run')

            experiment_cycles = [dirname for dirname in os.listdir(cycles_path)
                                 if re.match('[0-9]*T[0-9]*Z', dirname)]

            for cycle in experiment_cycles:
                cycle_results = experiment_results[cycle] = {}

                with open(os.path.join(cycles_path, cycle, 'jedi_log_analysis.txt'), 'r') as f:
                    lines = f.readlines()

                for line in lines:
                    delim_chars = [':', '=']
                    for char in delim_chars:
                        if char in line:
                            key = line.split(char)[0].strip()
                            val = line.split(char)[1].strip()

                            cycle_results[key] = val
            
            all_results[str(i)] = experiment_results

        formatted_results = {}

        for exp_num, experiment_results in all_results.items():
            cycles = experiment_results.keys()

            for cycle in cycles:
                if cycle not in formatted_results:
                    formatted_results[cycle] = {}

                for key, val in experiment_results[cycle]:
                    if key not in formatted_results[cycle].keys():
                        formatted_results[cycle][key] = np.empty(len(all_results.keys()))
                        formatted_results[cycle][key] = np.nan
                    else:
                        formatted_results[cycle][key][exp_num] = val

        output_string = ''
        
        for cycle in formatted_results.keys():
            header = [cycle].extend(['exp%d'%(exp_num) for exp_num in range(len(experiment_paths))])

            widths = [''] + np.zeros(len(formatted_results[cycle].keys()))

            rows = [header]
            for key, val in formatted_results[cycle].keys():
                row = [key].extend(val)

                for i, item in enumerate(row):
                    widths[i] = max(len(item), widths(i))

                rows.append(row)
            
            for row in rows:
                for item, width in zip(row, widths):
                    add_len = width - len(item) + 2
                    output_string += item + add_len
                output_string += '\n'

        print(output_string)

# --------------------------------------------------------------------------------------------------