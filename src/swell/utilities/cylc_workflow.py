# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from typing import Union, Optional, Self, Tuple
from collections.abc import Mapping

from swell.utilities.cylc_formatting import CylcSection, indent_lines
from swell.tasks.task_runtimes import TaskRuntimes

# --------------------------------------------------------------------------------------------------

class CylcWorkflow():

    ''' 
    Handles generating the flow.cylc file contents using the CylcSection syntax for each
    necessary section in the cylc file. Since Swell workflows share a lot of common language,
    this method has the convenience of automatically setting a lot of the contents. This means
    that the graph section is the only part that will need to be adjusted in many cases, 
    and tasks may need to be altered in src/swell/tasks/task_runtimes.py.
    '''

    def __init__(self, experiment_dict, slurm_external) -> None:
        self.experiment_dict = experiment_dict
        self.slurm_external = slurm_external

        self.setup_workflow()

    # --------------------------------------------------------------------------------------------------

    def set_experiment_dict(self, experiment_dict) -> None:
        self.experiment_dict = experiment_dict

    # --------------------------------------------------------------------------------------------------

    def format_string_block(self, string) -> str:
        out_string = '"""\n'
        out_string += indent_lines(string, 1, True)
        out_string += '"""\n'

        return out_string

    # --------------------------------------------------------------------------------------------------

    def format_cycle(self, name: str, cycle: str) -> str:
        cycle_string = f'{name} = '
        cycle_string += self.format_string_block(cycle)
        return cycle_string

    # --------------------------------------------------------------------------------------------------
    
    def reset_indentation(self, string: str) -> str:
        out_string = ''

        start = False
        for line in string.split('\n'):
            line = line.strip()

            if len(line) > 0:
                start = True

            if start:
                out_string += line

        return out_string

    # --------------------------------------------------------------------------------------------------
    
    def setup_workflow(self) -> None:
        self.header = self.define_header()
        self.description = self.define_description()
        self.scheduler = self.define_scheduler()

        self.scheduling_section = self.define_scheduling_section()
        self.graph_section = self.define_graph_section()

        self.scheduling = self.define_scheduling()

        self.tasks = self.parse_graph_for_tasks()
        print(self.tasks)

    # --------------------------------------------------------------------------------------------------

    def define_header(self) -> str:
        header = self.comment_block(string = """
                # (C) Copyright 2021- United States Government as represented by the Administrator of the
                # National Aeronautics and Space Administration. All Rights Reserved.
                #
                # This software is licensed under the terms of the Apache Licence Version 2.0
                # which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.""")

        return header
    
    def define_description(self) -> str:
        description = self.comment_block("""# Cylc workflow auto-generated for suite {suite_to_run} by Swell.""".format(**self.experiment_dict))
        return description

    # --------------------------------------------------------------------------------------------------

    def comment_block(self, string, level: int = 0, section_break: bool = True):
        out_string = ''

        string = indent_lines(string, level, reset=True)

        start = False
        for line in string.split('\n'):
            if len(line.strip()) > 0:
                start = True

            if start:
                out_string += f'{line}\n'

        if section_break:
            out_string += f'\n# {"-" *98}\n\n'

        return out_string

    # --------------------------------------------------------------------------------------------------


    def define_scheduler(self) -> str:
        scheduler_dict = {'UTC mode': True, 'allow implicit tasks': False}
        scheduler = self.create_new_section('scheduler', scheduler_dict)

        return scheduler.get_section_str()

    # --------------------------------------------------------------------------------------------------
    
    def define_scheduling(self) -> str:
        scheduling = self.define_scheduling_section()
        graph = self.define_graph_section()

        scheduling.add_subsection(graph)

        return scheduling.get_section_str()

    # --------------------------------------------------------------------------------------------------
    
    def define_scheduling_section(self) -> CylcSection:
        scheduling_dict = {'initial cycle point': self.experiment_dict['start_cycle_point'],
                           'final cycle point': self.experiment_dict['final_cycle_point'],
                           'runahead limit': self.experiment_dict['runahead_limit']}
        
        scheduling_section = self.create_new_section('scheduling', scheduling_dict)

        return scheduling_section

    # --------------------------------------------------------------------------------------------------

    def define_graph_section(self) -> CylcSection:
        return self.create_new_section('graph')

    # --------------------------------------------------------------------------------------------------
    
    def parse_graph_for_tasks(self) -> CylcSection:
        tasks = []

        cylc_characters = [':', '[', ']', '?']
        
        in_graph = False
        in_cycle = False

        for line in self.scheduling.split('\n'):
            comment = False
            sub_strings = line.split(' ')

            for sub_string in sub_strings:
                sub_string = sub_string.strip()

                if '#' in sub_string:
                    comment = True

                if not comment and in_graph and in_cycle:
                    if len(sub_string) > 0 and sub_string not in ['=>', '&', '|', '"""']:
                        task = sub_string
                        for i, char in enumerate(task):
                            if char in cylc_characters:
                                task = task.split(char)[0]

                        if len(task) > 0 and task not in tasks:
                            tasks.append(task)

                if '"""' in sub_string:
                    in_cycle = not in_cycle

            if '[graph]' in line:
                in_graph = True

        return tasks

    # --------------------------------------------------------------------------------------------------
    
    def get_independent_and_model_tasks(self) -> Tuple[list, dict]:
        ind_tasks = []
        model_tasks = {}

        models = []
        if 'model_components' in self.experiment_dict:
            models = self.experiment_dict['model_components']
        else:
            models = []

        for model in models:
            model_tasks[model] = []

        for task in self.tasks:
            if '-' in task:
                task_name = task.split('-')[0]
                model = task.split('-')[1]

                if model in models:
                    model_tasks[model].append(task_name)
            else:
                ind_tasks.append(task)

        return ind_tasks, model_tasks

    # --------------------------------------------------------------------------------------------------
    
    def define_runtime_task_overrides(self) -> dict:
        return {}

    # --------------------------------------------------------------------------------------------------
    
    def create_new_section(self, name: Optional[str] = None, content: Union[str, dict] = ''):
        return CylcSection(name, content)

    # --------------------------------------------------------------------------------------------------
    
    def define_runtime(self) -> str:
        runtime_section = self.create_new_section('runtime', '\n# Task defaults\n# -------------\n')

        runtime_overrides = self.define_runtime_task_overrides()

        for task in ['root'] + self.tasks:
            if task in runtime_overrides.keys():
                task_section = self.define_runtime_task_overrides[task]

                runtime_section.add_subsection(task_section)

            else:
                if '-' in task:
                    task_name = task.split('-')[0]
                    model = task.split('-')[1]
                    if model not in self.experiment_dict['model_components']:
                        task_name = task
                        model = None
                else:
                    task_name = task
                    model = None
                    
                task_class = TaskRuntimes.get(task_name)
                task_section = task_class(model=model).get_section(self.experiment_dict, self.slurm_external)

                runtime_section.add_subsection(task_section)

        runtime_str = runtime_section.get_section_str()

        return runtime_str

    # --------------------------------------------------------------------------------------------------

    def get_workflow_str(self) -> str:

        workflow_str = ''

        workflow_str += self.header
        workflow_str += self.description
        workflow_str += self.scheduler
        workflow_str += self.scheduling

        runtime = self.define_runtime()
        workflow_str += runtime

        return workflow_str

    # --------------------------------------------------------------------------------------------------
