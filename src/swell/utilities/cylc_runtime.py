# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import yaml
from typing import Union, Optional
from collections.abc import Mapping
from dataclasses import dataclass

from swell.utilities.cylc_formatting import CylcSection, indent_lines
from swell.utilities.suite_utils import get_model_components
from swell.utilities.dictionary import update_dict
from swell.utilities.dataclass_utils import mutable_field

# --------------------------------------------------------------------------------------------------


@dataclass
class Task:

    '''
    Contains the basic properties and information needed to format the cylc [runtime] section.
    '''

    base_name: Optional[str] = None
    scheduling_name: Optional[str] = None

    model: Optional[str] = None

    pre_script: Union[str, bool, None] = False
    script: Union[str, bool, None] = None

    retry: Union[str, Mapping, None] = None
    time_limit: Union[str, Mapping, None] = None
    environment: Optional[Mapping] = None
    slurm: Optional[Mapping] = None

    is_cycling: bool = False
    is_model: bool = False

    additional_sections: list = mutable_field([])
    mail_events: list = mutable_field(['failed', 'submit-failed'])

    # --------------------------------------------------------------------------------------------------

    def __post_init__(self):

        if self.base_name is None:
            self.base_name = self.__class__.__name__

        if self.scheduling_name is None:
            self.scheduling_name = self.base_name

            if self.is_model and self.model is not None:
                self.scheduling_name += f'-{self.model}'

        if self.script is None:
            self.script = f'swell task {self.base_name} $config'

            if self.is_cycling:
                self.script += ' -d $datetime'

            if self.is_model and self.model is not None:
                self.script += ' -m {model}'

        if self.is_model and self.model is not None:
            self.script = self.script.format(model=self.model)
            self.scheduling_name = self.scheduling_name.format(model=self.model)

    # --------------------------------------------------------------------------------------------------

    def format_string_block(self, string: str) -> str:
        out_string = '"""\n'
        out_string += indent_lines(string, 1)
        out_string += '"""'

        return out_string

    # --------------------------------------------------------------------------------------------------

    def match_platform(self, content: Union[str, dict], platform: str):
        # Resolve platform-specific entries in the task object

        if isinstance(content, Mapping):
            if platform in content.keys():
                content = content[platform]
            elif 'all' in content.keys():
                content = content['all']

        return content

    # --------------------------------------------------------------------------------------------------

    def create_new_section(self,
                           name: Optional[str] = None,
                           content: Union[str, dict] = ''
                           ) -> CylcSection:
        return CylcSection(name, content)

    # --------------------------------------------------------------------------------------------------

    def resolve_model(self, slurm_dict: Mapping) -> dict:
        ''' Resolve "all" and "model" entries in slurm dictionary '''
        if 'all' in slurm_dict.keys() and isinstance(slurm_dict['all'], Mapping):
            slurm_dict = update_dict(slurm_dict, slurm_dict['all'])
            del slurm_dict['all']
        if self.model in slurm_dict.keys() and isinstance(slurm_dict[self.model], Mapping):
            slurm_dict = update_dict(slurm_dict, slurm_dict[self.model])

        for model in get_model_components():
            if model in slurm_dict.keys():
                del slurm_dict[model]

        return slurm_dict

    # --------------------------------------------------------------------------------------------------

    def generate_task_slurm_dict(self, slurm_external: Mapping, platform: str) -> Mapping:
        # Take the external slurm dictionary and merge it with the task's parameters
        # to get the dict that will be output in the flow.cylc

        slurm_dict = {}
        if self.slurm is not None:
            for key, value in self.slurm.items():
                slurm_dict[key] = self.match_platform(value, platform)

        slurm_globals = slurm_external['slurm_directives_global']
        slurm_task = {}

        if 'slurm_directives_tasks' in slurm_external.keys():
            task_directives = slurm_external['slurm_directives_tasks']

            if self.base_name in task_directives:
                slurm_task = task_directives[self.base_name]
            if self.scheduling_name in task_directives:
                slurm_task = task_directives[self.scheduling_name]

        slurm_dict = {'job-name': self.scheduling_name,
                      **self.resolve_model(slurm_globals),
                      **self.resolve_model(slurm_dict),
                      **self.resolve_model(slurm_task)}

        return slurm_dict

    # --------------------------------------------------------------------------------------------------

    def get_section(self, experiment_dict: Mapping, slurm_external: Mapping):
        ''' Return the runtime section for the given task. '''

        platform = experiment_dict['platform']
        runtime_dict = {}

        # Set the pre_script only if it is specified
        if self.pre_script:
            runtime_dict['pre-script'] = self.format_string_block(self.pre_script)

        # Set the script
        if self.script:
            script_str = self.script

            if 'pause_on_tasks' in experiment_dict.keys():
                if len(set([self.base_name, self.scheduling_name])
                       & set(experiment_dict['pause_on_tasks'])) > 0:
                    script_str += '\ncylc pause $CYLC_WORKFLOW_ID'

            runtime_dict['script'] = self.format_string_block(script_str)

        # Specify the platform if this is a slurm task
        if self.slurm is not None:
            runtime_dict['platform'] = platform

        # Set the time limit, default is 1 hour
        if self.time_limit is True:
            runtime_dict['execution time limit'] = 'PT1H'
        elif self.time_limit:
            time_limit = self.match_platform(self.time_limit, platform)
            runtime_dict['execution time limit'] = time_limit

        # Set the retry if this task needs it
        if self.retry:
            if self.retry is True:
                retry = '2*PT1M'
            else:
                retry = self.match_platform(self.retry, platform)

            runtime_dict['execution retry delays'] = retry

        runtime_section = self.create_new_section(self.scheduling_name, runtime_dict)

        # Set the environment dictionary
        if self.environment is not None:
            environment_section = self.create_new_section('environment', self.environment)
            runtime_section.add_subsection(environment_section)

        # Specify the slurm dictionary with defaults from user and global settings
        if self.slurm is not None:

            slurm_dict = self.generate_task_slurm_dict(slurm_external, platform)

            slurm_section_dict = {}
            for key, value in slurm_dict.items():
                slurm_section_dict[f'--{key}'] = value

            directive_section = self.create_new_section('directives', slurm_section_dict)

            runtime_section.add_subsection(directive_section)

        # Append additional sections to runtime
        for section in self.additional_sections:
            runtime_section.add_subsection(section)

        # Check slurm messaging parameters
        events = []
        if 'task_email_parameters' in experiment_dict.keys():
            if experiment_dict['task_email_parameters'] == 'auto':
                # Set message status to fail or event fail
                events = self.mail_events
            elif self.scheduling_name in experiment_dict['task_email_parameters'].keys():
                events = experiment_dict['task_email_parameters'][self.scheduling_name]
            elif self.base_name in experiment_dict['task_email_parameters'].keys():
                events = experiment_dict['task_email_parameters'][self.base_name]

        # Add messaging section
        settings_file = os.path.expanduser(os.path.join('~', '.swell', 'swell-settings.yaml'))
        if os.path.exists(settings_file) and len(events) > 0:
            with open(settings_file, 'r') as f:
                settings_dict = yaml.safe_load(f)
            if 'email_address' in settings_dict.keys():
                email_address = settings_dict['email_address']
                address_section = self.create_new_section('mail', f'to = {email_address}')
                runtime_section.add_subsection(address_section)

                event_str = "{% if environ['SWELL_SEND_MESSAGES'] %}\n"
                event_str += "mail events = " + ', '.join(events)
                event_str += "\n{% endif %}\n"

                event_section = self.create_new_section('events', event_str)
                runtime_section.add_subsection(event_section)

        return runtime_section

# --------------------------------------------------------------------------------------------------
