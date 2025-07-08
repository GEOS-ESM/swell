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


class Workflow_compare_jedi(CylcWorkflow):

    # --------------------------------------------------------------------------------------------------

    def define_description(self):
        description = self.comment_block("""
        # Cylc suite for running comparison tests on completed experiments
        """)

        return description

    # --------------------------------------------------------------------------------------------------

    def define_scheduling(self):

        paths = self.experiment_dict['comparison_experiment_paths']

        if len(paths) < 2:
            self.logger.info('Please specify two experiments')

        scheduling_section = self.create_new_section('scheduling')

        r1_str = ''
        dependency_str = ''
        for i in range(len(paths)):
            r1_str += f"JediCTest-{i}\n"
            dependency_str += f"JediCTest-{i} & "

        dependency_str = dependency_str[:-3]
        dependency_str += ' => CompareJediCTestOutput\n'

        r1_str += dependency_str

        graph_str = self.format_cycle('R1', r1_str)

        graph_section = self.create_new_section('graph', graph_str)
        scheduling_section.add_subsection(graph_section)

        return scheduling_section.get_section_str()

    # --------------------------------------------------------------------------------------------------

    def define_runtime_task_overrides(self):
        overrides = {}

        exp_root = os.path.expandvars(self.experiment_dict['experiment_root'])
        exp_id = os.path.expandvars(self.experiment_dict['experiment_id'])

        output_dir = os.path.join(exp_root, exp_id)

        for i, path in enumerate(self.experiment_dict['comparison_experiment_paths']):
            config_file = os.path.join(os.path.dirname(path), 'experiment.yaml')
            overrides[f'JediCTest-{i}'] = Task(
                    base_name=f'JediCTest',
                    scheduling_name=f'JediCTest-{i}',
                    script=f'swell task JediCTest {config_file} -i {i} -o {output_dir}',
                    slurm={})

        return overrides
