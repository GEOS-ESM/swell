# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from typing import Union, Optional, Self
from collections.abc import Mapping
from dataclasses import dataclass

from swell.utilities.cylc_formatting import CylcSection, indent_lines

# --------------------------------------------------------------------------------------------------

indent = '    '

@dataclass
class Task:
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

    def __post_init__(self):

        if self.base_name is None:
            self.base_name = self.__class__.__name__

        if self.scheduling_name is None:
            self.scheduling_name = self.base_name

            if self.is_model:
                self.scheduling_name += f'-{self.model}'

        elif self.is_model:
            self.scheduling_name = self.scheduling_name.format(model = self.model)

        if self.script is None:
            self.script = f'swell task {self.base_name} $config'

            if self.is_cycling:
                self.script += ' -d $datetime'

            if self.is_model:
                self.script += f' -m {self.model}'

    def format_string_block(self, string: str) -> str:
        out_string = '"""\n'
        out_string += indent_lines(string, 1)
        out_string += '"""'

        return out_string
    
    def match_platform(self, content: Union[str, dict], platform: str):
        if isinstance(content, Mapping):
            if platform in content.keys():
                content = content[platform]
            elif 'all' in content.keys():
                content = content['all']
        
        return content

    def create_new_section(self, name: Optional[str] = None, content: Union[str, dict] = '') -> CylcSection:
        return CylcSection(name, content)

    def get_section(self, experiment_dict: Mapping, slurm_external: Mapping):
        platform = experiment_dict['platform']
        runtime_dict = {}

        if self.pre_script:
            runtime_dict['pre-script'] = self.format_string_block(self.pre_script)

        if self.script:
            runtime_dict['script'] = self.format_string_block(self.script)

        if self.slurm:
            runtime_dict['platform'] = platform

        if self.time_limit is True:
            runtime_dict['execution time limit'] = 'PT1H'
        elif self.time_limit:
            time_limit = self.match_platform(self.time_limit, platform)
            runtime_dict['execution time limit'] = time_limit

        if self.retry is True:
            runtime_dict['execution retry delays'] = '2*PT1M'
        if self.retry:
            retry = self.match_platform(self.retry, platform)
            runtime_dict['execution retry delays'] = retry

        runtime_section = self.create_new_section(self.scheduling_name, runtime_dict)

        if self.environment is not None:
            environment_section = self.create_new_section('environment', self.environment)
            runtime_section.add_subsection(environment_section)

        if self.slurm is not None:
            slurm_dict = {}
            for key, value in self.slurm.items():
                slurm_dict[key] = self.match_platform(value, platform)
            else:
                slurm_dict = {}

            slurm_globals = slurm_external['slurm_directives_global']
            slurm_task = {}

            if 'slurm_directives_tasks' in slurm_external.keys():
                task_directives = slurm_external['slurm_directives_tasks']

                if self.base_name in task_directives:
                    slurm_task = task_directives[self.base_name]
                if self.scheduling_name in task_directives:
                    slurm_task = task_directives[self.scheduling_name]
            else:
                slurm_task = {}

            slurm_dict = {'job-name': self.scheduling_name,
                          **slurm_globals,
                          **slurm_dict,
                          **slurm_task
                        }

            slurm_section_dict = {}
            for key, value in slurm_dict.items():
                slurm_section_dict[f'--{key}'] = value
            directive_section = self.create_new_section('directives', slurm_section_dict)
        
            runtime_section.add_subsection(directive_section)

        return runtime_section

# --------------------------------------------------------------------------------------------------

@dataclass
class Model(Task):
    def __post_init__(self):
        self.is_model = True
        super().__post_init__()

# --------------------------------------------------------------------------------------------------

@dataclass
class Cycling(Task):
    def __post_init__(self):
        self.is_cycling = True
        super().__post_init__()

# --------------------------------------------------------------------------------------------------

@dataclass
class Slurm(Task):
    def __post_init__(self):
        if not self.slurm:
            self.slurm = {}

        super().__post_init__()

# --------------------------------------------------------------------------------------------------
