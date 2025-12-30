# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from abc import abstractmethod, ABC

from swell.utilities.cylc_formatting import CylcSection, indent_lines
from swell.utilities.suite_utils import get_model_components
from swell.utilities.dictionary import update_dict
from swell.utilities.swell_questions import QuestionList
from swell.utilities.settings import read_settings

# --------------------------------------------------------------------------------------------------


class TaskSetup(ABC):

    '''
    Contains the basic properties and information needed to format the cylc [runtime] section.

    Attributes:
    model: model the task is being run under at runtime
    platform: platform the task is being run on

    base_name: basic name of the task within Swell
    scheduling_name: name for the task within cylc
    is_cycling: boolean for whether the task is run on cycles
    is_model: boolean for whether the task is run on a certain model
    pre_script: cylc setting for scripts run before the main script
    script: string of shell code to be run by cylc for the task
    retry: times * time interval cylc should retry the task, e.g. 2*PT10s
    time_limit: execution time limit for slurm
    slurm: dictionary of slurm parameters
    mail events: list of events for email messaging through cylc
    question_list: list of questions keys used by the task
    additional_sections: list of additional CylcSection objects to append to the runtime section
    '''

    def __init__(self, model: str | None = None, platform: str | None = None) -> None:

        self.model = model
        self.platform = platform

        self.base_name = None
        self.scheduling_name = None

        self.is_cycling = False
        self.is_model = False

        self.pre_script = False
        self.script = None

        self.retry = None
        self.time_limit = None
        self.slurm = None

        self.mail_events = ['failed', 'submit-failed']

        self.questions = []
        self.additional_sections = []

        self.set_attributes()
        self.post_init()

    # --------------------------------------------------------------------------------------------------

    @abstractmethod
    def set_attributes(self) -> None:
        '''Abstract method to be overridden by each task in order to set attributes.
        '''
        pass

    # --------------------------------------------------------------------------------------------------

    def post_init(self):
        '''Sets and resolves defaults for tasks after assignment
        '''

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

        # Set retry defaults
        if self.retry is True:
            self.retry = '2*PT1M'
        else:
            self.retry = self.match_platform(self.retry)

        # Set time limit defaults
        if self.time_limit is True:
            self.time_limit = 'PT1H'
        elif self.time_limit:
            self.time_limit = self.match_platform(self.time_limit)

        # Convert questions list into object
        self.question_list = QuestionList(self.questions)

    # --------------------------------------------------------------------------------------------------

    def format_string_block(self, string: str) -> str:
        """Format a string block with indentation for use in cylc.

        Arguments:
        string: string to be placed in quotes and indented

        Returns:
        Indented and quoted string.
        """
        out_string = '"""\n'
        out_string += indent_lines(string, 1)
        out_string += '"""'

        return out_string

    # --------------------------------------------------------------------------------------------------

    def match_platform(self, content: str | dict):
        '''Resolve platform-specific entries in mapping.

        Arguments:
        content: string or mapping containing platform-designated entries

        Returns:
        content filtered by the current platform, if specified

        Examples:
        >>> self.match_platform('a')
        'a'

        self.platform = 'nccs_discover_sles15'
        >>> self.match_platform({'nccs_discover_sles15': 'a', 'nccs_discover_cascade': 'b'})
        'a'
        '''

        if isinstance(content, Mapping):
            if self.platform in content.keys():
                content = content[self.platform]
            elif 'all' in content.keys():
                content = content['all']

        return content

    # --------------------------------------------------------------------------------------------------

    def create_new_section(self,
                           name: str | None = None,
                           content: str | dict = ''
                           ) -> CylcSection:
        '''Create and retrun a new CylcSection object for use in formatting.

        Arguments:
        name: Name of cylc section to be created
        content: string or dictionary of contents for the section
        '''
        return CylcSection(name, content)

    # --------------------------------------------------------------------------------------------------

    def resolve_model(self, slurm_dict: Mapping) -> dict:
        '''Resolve model-specific entries in slurm dictionary specification, if they exist.

        Arguments:
        slurm_dict: dictionary of slurm settings

        Returns:
        dictionary of slurm settings with any model-specific defaults resolved

        Examples:
        >>> self.model = 'geos_marine'
        >>> self.resolve_model({'time': '01:00:00', 'nodes': {'geos_atmosphere': 1, 'geos_marine': 3}})

        {'time': '01:00:00', 'nodes': 3}
        '''  # noqa
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

    def generate_task_slurm_dict(self, slurm_external: Mapping) -> Mapping:
        '''Take the external slurm dictionary and merge it with the task's parameters
        to get the dict that will be output in the runtime section

        Arguments:
        slurm_external: dictionary from `utilities/slurm.py` with defaults from the
                        platform and user.

        Returns:
        Finalized dictionary of slurm defaults for the task.
        '''

        slurm_dict = {}
        if self.slurm is not None:
            for key, value in self.slurm.items():
                slurm_dict[key] = self.match_platform(value)

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

    def runtime_string(self, experiment_dict: Mapping, slurm_external: Mapping) -> str:
        '''Return the runtime section for the given task.

        Constructs a CylcSection object by filling in a dictionary with the following components
        from the task:

        1) pre-script
        2) script
        3) platform
        4) execution time limit
        5) execution retry delays
        6) slurm subsection
        7) any additional subsections

        The CylcSection's contents is then converted into a string

        Arguments:
        experiment_dict: experiment dictionary from `create_experiment`
        slurm_external: external slurm defaults from globals and user defaults

        Returns:
        String to place in flow.cylc.
        '''

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

        if self.time_limit is not None:
            runtime_dict['execution time limit'] = self.time_limit

        # Set the retry if this task needs it
        if self.retry:
            runtime_dict['execution retry delays'] = self.retry

        runtime_section = self.create_new_section(self.scheduling_name, runtime_dict)

        # Specify the slurm dictionary with defaults from user and global settings
        if self.slurm is not None:

            slurm_dict = self.generate_task_slurm_dict(slurm_external)

            slurm_section_dict = {}
            for key, value in slurm_dict.items():
                slurm_section_dict[f'--{key}'] = value

            directive_section = self.create_new_section('directives', slurm_section_dict)

            runtime_section.add_subsection(directive_section)

        # Append additional sections to runtime
        for section in self.additional_sections:
            runtime_section.add_subsection(section)

        # Check slurm messaging parameters
        events = self.mail_events

        settings_dict = read_settings()

        # Add messaging section
        if len(events) > 0 and 'email_address' in settings_dict.keys():
            email_address = settings_dict['email_address']
            address_section = self.create_new_section('mail', f'to = {email_address}')
            runtime_section.add_subsection(address_section)

            event_str = "{% if environ['SWELL_SEND_MESSAGES'] %}\n"
            event_str += "mail events = " + ', '.join(events)
            event_str += "\n{% endif %}\n"

            event_section = self.create_new_section('events', event_str)
            runtime_section.add_subsection(event_section)

        runtime_string = runtime_section.get_section_str(level=1)

        runtime_string += '    # ' + '-' * 96 + '\n\n'

        return runtime_string

# --------------------------------------------------------------------------------------------------
