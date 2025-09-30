# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import re
import numpy as np

from swell.tasks.base.task_base import taskBase

# --------------------------------------------------------------------------------------------------

comparison_fields = {'Residual norm': {'delimiter': '=', 'dtype': float}}

# --------------------------------------------------------------------------------------------------


class JediLogComparison(taskBase):

    def execute(self):

        tolerances = {}
        for number in range(self.config.number_of_iterations()):
            tolerances['Residual norm ( {number})'] = 0.01

        # Construct dictionary for all results from log file
        all_results = {}

        # Boolean for whether fields fall within tolerances
        passed = True

        experiment_paths = self.config.comparison_experiment_paths()

        for exp_num, experiment_path in enumerate(experiment_paths):

            # Paths to cycle dirs
            cycles_path = os.path.join(os.path.dirname(experiment_path), '..', 'run')

            experiment_cycles = [dirname for dirname in os.listdir(cycles_path)
                                 if re.match('[0-9]*T[0-9]*Z', dirname)]

            for cycle in experiment_cycles:
                if cycle not in all_results.keys():
                    cycle_results = all_results[cycle] = {}

                cycle_log_file = os.path.join(cycles_path, cycle, self.get_model(),
                                              'jedi_variational_log.log')
                with open(cycle_log_file, 'r') as f:
                    lines = f.readlines()

                for line in lines:
                    for field_name in comparison_fields.keys():
                        field = comparison_fields[field_name]
                        if field_name in line:
                            key_val = line.split(field['delimiter'])
                            key = key_val[0].strip()
                            val = key_val[1].strip()

                            # val = field['dtype'](val)

                            if key not in cycle_results.keys():
                                cycle_results[key] = {f'exp{exp_num}': val}
                            else:
                                cycle_results[key][f'exp{exp_num}'] = val

                for key in cycle_results.keys():
                    for field_name in comparison_fields.keys():
                        if field_name in key:
                            dtype = comparison_fields[field_name]['dtype']

                            if dtype == float:
                                if 'exp0' in cycle_results[key] and 'exp1' in cycle_results[key]:
                                    diff = float(cycle_results[key]['exp0']) - \
                                            float(cycle_results[key]['exp1'])
                                    cycle_results[key]['diff'] = str(diff)
                                    if key in tolerances:
                                        key_passed = np.abs(diff) < tolerances[key]
                                        cycle_results[key]['pass'] = key_passed
                                    else:
                                        cycle_results[key]['pass'] = ''

                                    if not key_passed:
                                        passed = False
                            else:
                                cycle_results[key]['diff'] = 'N/A'
                                cycle_results[key]['pass'] = ''

        widths = {'key': len(cycle), 'exp0': 0, 'exp1': 0, 'diff': 0, 'pass': 0}

        for cycle, cycle_results in all_results.items():
            for key in cycle_results:
                if 'exp0' not in cycle_results[key]:
                    cycle_results[key]['exp0'] = 'N/A'
                if 'exp1' not in cycle_results[key]:
                    cycle_results[key]['exp1'] = 'N/A'
                if 'diff' not in cycle_results[key]:
                    cycle_results[key]['diff'] = 'N/A'
                if 'pass' not in cycle_results[key]:
                    cycle_results[key]['pass'] = False
                    passed = False

                widths['key'] = max(widths['key'], len(key))
                widths['exp0'] = max(widths['exp0'], len(cycle_results[key]['exp0']))
                widths['exp1'] = max(widths['exp1'], len(cycle_results[key]['exp1']))
                widths['diff'] = max(widths['diff'], len(str(cycle_results[key]['diff'])))

        for key, val in widths.items():
            widths[key] = val + 2

        out_string = '\n'
        out_string += f'exp0: {experiment_paths[0]}\n'
        out_string += f'exp1: {experiment_paths[1]}\n'
        out_string += '\n'

        for cycle, cycle_results in all_results.items():
            out_string += cycle + ' ' * (widths['key'] - len(cycle))
            out_string += 'exp0' + ' ' * (widths['exp0'] - len('exp0'))
            out_string += 'exp1' + ' ' * (widths['exp1'] - len('exp1'))
            out_string += 'diff' + ' ' * (widths['diff'] - len('diff'))
            out_string += 'pass' + ' ' * (widths['pass'] - len('pass'))

            out_string += '\n'

            for key in tolerances.keys():
                val_dict = cycle_results[key]

                out_string += key + ' ' * (widths['key'] - len(key))
                out_string += val_dict['exp0'] + ' ' * (widths['exp0'] - len(val_dict['exp0']))
                out_string += val_dict['exp1'] + ' ' * (widths['exp1'] - len(val_dict['exp1']))
                out_string += val_dict['diff'] + ' ' * (widths['diff'] - len(val_dict['diff']))
                out_string += str(val_dict['pass']) + ' ' * (
                        widths['pass'] - len(str(val_dict['pass'])))
                out_string += '\n'

            out_string += '\n'

        self.logger.info(out_string)

        with open(os.path.join(self.experiment_path(), 'jedi_log_comparison.txt'), 'w') as f:
            f.write(out_string)

        if not passed:
            self.logger.abort(f'Parameters not within tolerance')

# --------------------------------------------------------------------------------------------------
