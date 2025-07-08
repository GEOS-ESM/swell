# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import yaml
import os

from swell.utilities.cylc_workflow import CylcWorkflow
from swell.tasks.task_runtimes import TaskRuntimes
from swell.utilities.cylc_runtime import Task

# --------------------------------------------------------------------------------------------------


class Workflow_compare_variational(CylcWorkflow):

    # --------------------------------------------------------------------------------------------------

    def define_description(self):
        description = self.comment_block("""
        # Cylc suite for running comparison tests on completed experiments
        """)

        return description

    # --------------------------------------------------------------------------------------------------

    def define_scheduling(self):

        paths = self.experiment_dict['comparison_experiment_paths']

        if len(paths) > 0:
            config_file = os.path.join(os.path.dirname(paths[0]), 'experiment.yaml')
            with open(config_file, 'r') as f:
                base_dict = yaml.safe_load(f)

            start_cycle_point = base_dict['start_cycle_point']
            final_cycle_point = base_dict['final_cycle_point']

            cycle_model_times = {}

            for model in base_dict['models'].keys():
                cycle_times = base_dict['models'][model]['cycle_times']
                for cycle_time in cycle_times:
                    if cycle_time not in cycle_model_times:
                        cycle_model_times[cycle_time] = []
                    cycle_model_times[cycle_time].append(model)
        else:
            start_cycle_point = 'None'
            final_cycle_point = 'None'
            cycle_model_times = {}

            self.logger.info('No experiments have been specified')

        scheduling_section = self.create_new_section('scheduling',
                                                     {'initial cycle point': start_cycle_point,
                                                      'final cycle point': final_cycle_point})

        graph_str = ''

        for cycle_time, models in cycle_model_times.items():
            cycle_str = ''

            for model in models:
                for i in range(len(paths)):
                    cycle_str += f"FGrepResidualNorm-{model}-{i}\n"

            graph_str += self.format_cycle(cycle_time, cycle_str)

        graph_section = self.create_new_section('graph', graph_str)

        scheduling_section.add_subsection(graph_section)

        return scheduling_section.get_section_str()

    # --------------------------------------------------------------------------------------------------

    def define_runtime_task_overrides(self):
        overrides = {}

        exp_root = os.path.expandvars(self.experiment_dict['experiment_root'])
        exp_id = self.experiment_dict['experiment_id']

        output_dir = os.path.join(exp_root, exp_id)

        paths = self.experiment_dict['comparison_experiment_paths']

        for i, path in enumerate(paths):
            config_file = os.path.join(os.path.dirname(path), 'experiment.yaml')
            with open(config_file, 'r') as f:
                exp_dict = yaml.safe_load(f)

            for model in exp_dict['model_components']:
                overrides[f'FGrepResidualNorm-{model}-{i}'] = Task(
                        base_name='FGrepResidualNorm',
                        scheduling_name=(f'FGrepResidualNorm-{model}-{i}'),
                        script=(f'swell task FGrepResidualNorm {config_file} -d $datetime'
                                f' -m {model} -i {i} -o {output_dir}'))

        return overrides

# --------------------------------------------------------------------------------------------------
