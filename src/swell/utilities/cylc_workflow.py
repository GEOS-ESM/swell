# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from typing import Union, Optional, Tuple
from abc import abstractmethod

from swell.utilities.cylc_formatting import CylcSection, indent_lines
from swell.tasks.task_runtimes import TaskRuntimes
from swell.utilities.logger import get_logger
from swell.utilities.jinja2 import template_string_jinja2

# --------------------------------------------------------------------------------------------------


header_str = '''
#jinja2
# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------
'''


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

        self.logger = get_logger(self.__class__.__name__)

        self.initial_workflow_str = self.define_initial_workflow()
        self.tasks = self.parse_graph_for_tasks()

    # --------------------------------------------------------------------------------------------------

    def default_header(self) -> str:
        return header_str

    # --------------------------------------------------------------------------------------------------

    def format_string_block(self, string) -> str:
        # Format a string block with proper indentation

        out_string = '"""\n'
        out_string += indent_lines(string, 1, True)
        out_string += '"""\n'

        return out_string

    # --------------------------------------------------------------------------------------------------

    def format_cycle(self, name: str, cycle: str) -> str:
        # Format a cycle in the graph section

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
                out_string += line + '\n'

        return out_string

    # --------------------------------------------------------------------------------------------------

    @abstractmethod
    def define_initial_workflow(self) -> str:
        return ''

    # --------------------------------------------------------------------------------------------------

    def parse_graph_for_tasks(self) -> CylcSection:
        # Iterate through the graph section and determine all the tasks used by the suite

        tasks = []

        cylc_characters = [':', '[', ']', '?']

        in_graph = False
        in_cycle = False

        for line in self.initial_workflow_str.split('\n'):
            comment = False
            sub_strings = line.split(' ')

            for sub_string in sub_strings:
                sub_string = sub_string.strip()

                if sub_string.startswith('#'):
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
        # Separate the tasks into model independent and dependent

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

                for entry in task.split('-'):
                    if entry in models:
                        model_tasks[model].append(task_name)

            else:
                ind_tasks.append(task)

        return ind_tasks, model_tasks

    # --------------------------------------------------------------------------------------------------

    def define_runtime_task_overrides(self) -> dict:
        # Override in suite file to set any custom runtimes as needed by the suite
        return {}

    # --------------------------------------------------------------------------------------------------

    def create_new_section(self, name: Optional[str] = None, content: Union[str, dict] = ''):
        # Create a new section with indentation and content
        return CylcSection(name, content)

    # --------------------------------------------------------------------------------------------------

    def define_runtime(self) -> str:
        # Handle adding runtime sections for all tasks
        runtime_section = self.create_new_section('runtime', '\n# Task defaults\n# -------------\n')

        # Grab any overrides for certain tasks
        runtime_overrides = self.define_runtime_task_overrides()

        for task in ['root'] + self.tasks:
            if task in runtime_overrides.keys():
                task_section = runtime_overrides[task].get_section(
                        self.experiment_dict, self.slurm_external)

                runtime_section.add_subsection(task_section)

            else:
                if '-' in task:
                    task_name = task.split('-')[0]
                    model = task.split('-')[1]
                    if 'model_components' not in self.experiment_dict or (
                            model not in self.experiment_dict['model_components']):
                        task_name = task
                        model = None
                else:
                    task_name = task
                    model = None

                task_class = TaskRuntimes.get(task_name)
                task_section = task_class(model=model).get_section(
                        self.experiment_dict, self.slurm_external)

                runtime_section.add_subsection(task_section)

        runtime_str = runtime_section.get_section_str()

        return runtime_str

    # --------------------------------------------------------------------------------------------------

    def get_workflow_str(self) -> str:
        # Get the whole string to go into the flow.cylc file

        workflow_str = self.initial_workflow_str
        workflow_str = template_string_jinja2(logger=self.logger,
                                              templated_string=workflow_str,
                                              dictionary_of_templates=self.experiment_dict,
                                              allow_unresolved=False)

        workflow_str += '\n\n' + self.define_runtime()

        return workflow_str

    # --------------------------------------------------------------------------------------------------
