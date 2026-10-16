# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from ruamel.yaml import YAML
import os
import re
import numpy as np

from swell.tasks.base.task_base import taskBase
from swell.utilities.comparisons import comparison_tags

# --------------------------------------------------------------------------------------------------

comparison_fields = {'Residual norm': {'delimiter': '=', 'dtype': float}}

# --------------------------------------------------------------------------------------------------


class JediLogComparison(taskBase):

    def execute(self):

        experiment_paths = self.config.comparison_experiment_paths()

        experiment_tag_paths = comparison_tags(experiment_paths, self.logger)

        exp_tag_exp = list(experiment_tag_paths.keys())[0]
        exp_tag_ctl = list(experiment_tag_paths.keys())[1]

        experiment_path_exp = list(experiment_tag_paths.values())[0]
        experiment_path_ctl = list(experiment_tag_paths.values())[1]

        yaml = YAML(typ='safe')

        # Get the number of iterations between experiments
        iterations_list = []
        for path in experiment_tag_paths.values():
            with open(path, 'r') as f:
                exp_dict = yaml.load(f)
                num_iters = int(exp_dict['models'][self.get_model()]['number_of_iterations'][0])
                iterations_list.append(num_iters)

        number_of_iterations = min(iterations_list)

        tolerances = {}
        for number in range(number_of_iterations):
            tolerances[f'Residual norm ({number:>2})'] = 1e-5

        # Construct dictionary for all results from log file
        all_results = {}

        # Boolean for whether fields fall within tolerances
        passed = True

        log_type = self.config.comparison_log_type()

        for exp_tag, experiment_path in experiment_tag_paths.items():

            # Paths to cycle dirs
            cycles_path = os.path.join(os.path.dirname(experiment_path), '..', 'run')

            experiment_cycles = [dirname for dirname in os.listdir(cycles_path)
                                 if re.match('[0-9]*T[0-9]*Z', dirname)]

            experiment_cycles = sorted(experiment_cycles)

            # Don't look for logs from forecasting suites
            if log_type == 'fgat':
                experiment_cycles = experiment_cycles[:-1]

            for cycle in experiment_cycles:
                if cycle not in all_results.keys():
                    cycle_results = all_results[cycle] = {}
                else:
                    cycle_results = all_results[cycle]

                cycle_log_file = os.path.join(cycles_path, cycle, self.get_model(),
                                              f'jedi_{log_type}_log.log')
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
                                cycle_results[key] = {exp_tag: val}
                            else:
                                cycle_results[key][exp_tag] = val

                for key in cycle_results.keys():
                    for field_name in comparison_fields.keys():
                        if field_name in key:
                            dtype = comparison_fields[field_name]['dtype']

                            if dtype == float:
                                if exp_tag_exp in cycle_results[key] and exp_tag_ctl in \
                                        cycle_results[key]:
                                    diff = float(cycle_results[key][exp_tag_exp]) - \
                                            float(cycle_results[key][exp_tag_ctl])
                                    cycle_results[key]['diff'] = str(diff)
                                    if key in tolerances:
                                        key_passed = np.abs(diff) < tolerances[key]
                                        cycle_results[key]['pass'] = key_passed
                                    else:
                                        key_passed = True
                                        cycle_results[key]['pass'] = ''

                                    if not key_passed:
                                        passed = False
                            else:
                                cycle_results[key]['diff'] = 'N/A'
                                cycle_results[key]['pass'] = ''

        widths = {'key': len(cycle), exp_tag_exp: 0, exp_tag_ctl: 0, 'diff': 0, 'pass': 0}

        for cycle, cycle_results in all_results.items():
            for key in cycle_results:
                if exp_tag_exp not in cycle_results[key]:
                    cycle_results[key][exp_tag_exp] = 'N/A'
                if exp_tag_ctl not in cycle_results[key]:
                    cycle_results[key][exp_tag_ctl] = 'N/A'
                if 'diff' not in cycle_results[key]:
                    cycle_results[key]['diff'] = 'N/A'
                if 'pass' not in cycle_results[key]:
                    cycle_results[key]['pass'] = False
                    passed = False

                widths['key'] = max(widths['key'], len(key))
                widths[exp_tag_exp] = max(widths[exp_tag_exp], len(cycle_results[key][exp_tag_exp]))
                widths[exp_tag_ctl] = max(widths[exp_tag_ctl], len(cycle_results[key][exp_tag_ctl]))
                widths['diff'] = max(widths['diff'], len(str(cycle_results[key]['diff'])))

        for key, val in widths.items():
            widths[key] = val + 2

        out_string = '\n'
        out_string += f'{exp_tag_exp}: {experiment_path_exp}\n'
        out_string += f'{exp_tag_ctl}: {experiment_path_ctl}\n'
        out_string += '\n'

        for cycle, cycle_results in all_results.items():
            out_string += cycle + ' ' * (widths['key'] - len(cycle))
            out_string += exp_tag_exp + ' ' * (widths[exp_tag_exp] - len(exp_tag_exp))
            out_string += exp_tag_ctl + ' ' * (widths[exp_tag_ctl] - len(exp_tag_ctl))
            out_string += 'diff' + ' ' * (widths['diff'] - len('diff'))
            out_string += 'pass' + ' ' * (widths['pass'] - len('pass'))

            out_string += '\n'

            for key in tolerances.keys():
                if key in cycle_results:
                    val_dict = cycle_results[key]

                    out_string += key + ' ' * (widths['key'] - len(key))
                    out_string += val_dict[exp_tag_exp] + ' ' * (widths[exp_tag_exp] -
                                                               len(val_dict[exp_tag_exp]))
                    out_string += val_dict[exp_tag_ctl] + ' ' * (widths[exp_tag_ctl] -
                                                               len(val_dict[exp_tag_ctl]))
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
