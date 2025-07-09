# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from typing import Union, Optional, Tuple
import os
import yaml

from swell.utilities.cylc_formatting import CylcSection, indent_lines
from swell.tasks.task_runtimes import TaskRuntimes
from swell.utilities.dictionary import update_dict
from swell.utilities.logger import get_logger

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

        self.logger = get_logger(self.__class__.__name__)

        self.setup_workflow()

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
                out_string += line

        return out_string

    # --------------------------------------------------------------------------------------------------

    def setup_workflow(self) -> None:
        # Initial setup for the workflow, includes everything but the runtime section

        self.header = self.define_header()
        self.description = self.define_description()
        self.scheduler = self.define_scheduler()
        self.scheduling = self.define_scheduling()

        self.tasks = self.parse_graph_for_tasks()

    # --------------------------------------------------------------------------------------------------

    def define_header(self) -> str:
        # Define a 'header', usually this includes any copyright information

        header = '#!jinja2\n'
        header += self.comment_block(string="""
        # (C) Copyright 2021- United States Government as represented by the Administrator of the
        # National Aeronautics and Space Administration. All Rights Reserved.
        #
        # This software is licensed under the terms of the Apache Licence Version 2.0
        # which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.""")

        return header

    # --------------------------------------------------------------------------------------------------

    def define_description(self) -> str:
        description = self.comment_block(
                """# Cylc workflow auto-generated for suite {suite_to_run} by Swell."""
                .format(**self.experiment_dict))
        return description

    # --------------------------------------------------------------------------------------------------

    def comment_block(self, string, level: int = 0, section_break: bool = True):
        # Format a comment block with proper indentation

        out_string = ''

        string = indent_lines(string, level, reset=True)

        start = False
        for line in string.split('\n'):
            if len(line.strip()) > 0:
                start = True

            if start:
                out_string += f'{line}\n'

        if section_break:
            out_string += f'\n# {"-" * 98}\n\n'

        return out_string

    # --------------------------------------------------------------------------------------------------

    def define_scheduler(self) -> str:
        # Define a scheduler section that includes email infrastructure

        scheduler_str = 'UTC mode = True\nallow implicit tasks = False\n'

        settings_file = os.path.expanduser(os.path.join('~', '.swell', 'swell-settings.yaml'))
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings_dict = yaml.safe_load(f)
            if 'email_address' in settings_dict.keys():
                email_address = settings_dict['email_address']

                message_str = "{% if environ['SWELL_SEND_MESSAGES'] %}\n"
                message_str += '[[events]]\n'
                message_str += indent_lines('mail events = startup, shutdown\n', 1)
                message_str += '[[mail]]\n'
                message_str += indent_lines(f'to = {email_address}\n', 1)
                message_str += '{% endif %}\n'

                scheduler_str += message_str

        scheduler = self.create_new_section('scheduler', scheduler_str)

        return scheduler.get_section_str()

    # --------------------------------------------------------------------------------------------------

    def define_scheduling(self) -> str:
        # Get the string for the entire scheduling section

        scheduling = self.define_scheduling_section()
        graph = self.define_graph_section()

        scheduling.add_subsection(graph)

        return scheduling.get_section_str()

    # --------------------------------------------------------------------------------------------------

    def define_scheduling_section(self) -> CylcSection:
        # Define a CylcSection object that comprises the initial contents of the scheduling section
        # This will be appended to the graph section to create the overall section
        scheduling_dict = {'initial cycle point': self.experiment_dict['start_cycle_point'],
                           'final cycle point': self.experiment_dict['final_cycle_point']}

        if 'runahead_limit' in self.experiment_dict:
            scheduling_dict = update_dict(
                    scheduling_dict,
                    {'runahead limit': self.experiment_dict['runahead_limit']})

        scheduling_section = self.create_new_section('scheduling', scheduling_dict)

        return scheduling_section

    # --------------------------------------------------------------------------------------------------

    def define_graph_section(self) -> CylcSection:
        # Define a CylcSection object that will be used to build the scheduling section
        return self.create_new_section('graph')

    # --------------------------------------------------------------------------------------------------

    def parse_graph_for_tasks(self) -> CylcSection:
        # Iterate through the graph section and determine all the tasks used by the suite

        tasks = []

        cylc_characters = [':', '[', ']', '?']

        in_graph = False
        in_cycle = False

        for line in self.scheduling.split('\n'):
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

        workflow_str = ''

        workflow_str += self.header
        workflow_str += self.description
        workflow_str += self.scheduler
        workflow_str += self.scheduling

        runtime = self.define_runtime()
        workflow_str += runtime

        return workflow_str

    # --------------------------------------------------------------------------------------------------
