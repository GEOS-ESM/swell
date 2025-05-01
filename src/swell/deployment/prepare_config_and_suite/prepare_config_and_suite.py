# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import copy
import os
import yaml
from collections.abc import Mapping
from typing import Union, Tuple, Optional
from enum import StrEnum
import datetime

from swell.swell_path import get_swell_path
from swell.utilities.suite_utils import get_model_components
from swell.deployment.prepare_config_and_suite.question_and_answer_cli import GetAnswerCli
from swell.deployment.prepare_config_and_suite.question_and_answer_defaults import GetAnswerDefaults
from swell.utilities.dictionary import dict_get
from swell.utilities.logger import Logger
from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.dictionary import update_dict, add_dict
from swell.tasks.task_questions import TaskQuestions as task_questions
from swell.suites.all_suites import SuiteConfigs, Workflows
from swell.utilities.swell_questions import QuestionType


# --------------------------------------------------------------------------------------------------


"""
Preparation of the configuration happens in several steps. Note that the configuration determines
templates and construction of the flow.cylc file.

1. The user chooses the suite they wish to run.

2. The code then builds a list of suite questions that do not depend on the model. At around the
   same time the code determines all the tasks within that suite that do not depend on the model
   component. At that point all these questions are asked using the question client.

3. If there is some dependency on model component(s) in the flow.cylc then the code will ask the
   user which model components should be included. Then all the suite questions depending on the
   model will be... (TODO: incomplete description, see methods below)

"""


# --------------------------------------------------------------------------------------------------


class PrepareExperimentConfigAndSuite:

    # ----------------------------------------------------------------------------------------------

    def __init__(
        self,
        logger: Logger,
        suite: str,
        suite_config: str,
        platform: str,
        config_client: str,
        override: Union[str, dict, None]
    ) -> None:

        # Store local copy of the inputs
        self.logger = logger
        self.suite = suite
        self.suite_config = suite_config
        self.platform = platform
        self.override = override

        # Assign the client that will take care of providing responses
        if config_client.lower() == 'cli':
            self.config_client = GetAnswerCli()
        elif config_client.lower() == 'defaults':
            self.config_client = GetAnswerDefaults()

        # Big dictionary that contains all user responses as well a dictionary containing the
        # questions that were asked
        self.experiment_dict = {}
        self.comment_dict = {}

        # Add the datetime to the dictionary
        # ----------------------------------
        self.experiment_dict['datetime_created'] = datetime.datetime.today().strftime("%Y%m%d_%H%M%SZ")
        self.comment_dict['datetime_created'] = 'Datetime this file was created (auto added)'

        # Add the platform the dictionary
        # -------------------------------
        self.experiment_dict['platform'] = platform
        self.comment_dict['platform'] = 'Computing platform to run the experiment'

        # Add the suite_to_run to the dictionary
        # --------------------------------------
        self.experiment_dict['suite_to_run'] = suite
        self.comment_dict['suite_to_run'] = 'Record of the suite being executed'

        # Get list of all possible models
        self.possible_model_components = get_model_components()

        self.prepare_suite_question_dictionary()
        self.override_with_defaults(QuestionType.SUITE)
        self.override_with_external(QuestionType.SUITE)
        self.ask_questions_and_configure(QuestionType.SUITE)

    # ----------------------------------------------------------------------------------------------

    def configure_and_ask_task_questions(self) -> None:
        self.prepare_task_question_dictionary()
        self.override_with_defaults(QuestionType.TASK)
        self.override_with_external(QuestionType.TASK)
        self.ask_questions_and_configure(QuestionType.TASK)

        return self.experiment_dict, self.comment_dict

    # ----------------------------------------------------------------------------------------------

    def set_model_ind_tasks(self, tasks: list) -> None:
        self.model_ind_tasks = tasks

    # ----------------------------------------------------------------------------------------------

    def set_model_dep_tasks(self, model_task_dict: Mapping) -> None:
        self.model_dep_tasks = model_task_dict

    # ----------------------------------------------------------------------------------------------

    def get_experiment_dict(self) -> Mapping:
        return self.experiment_dict
    
    # ----------------------------------------------------------------------------------------------

    def get_workflow_file_str(self, slurm_dict):
        self.workflow.set_experiment_dict(self.experiment_dict, slurm_dict)
        self.workflow.set_runtime_str()

        self.workflow_str = self.workflow.get_workflow_str()

        return self.workflow_str

    # ----------------------------------------------------------------------------------------------


    def prepare_task_question_dictionary(self):
        for task in self.model_independent_tasks:
            if task in task_questions.get_all():
                if self.suite_needs_model_components:
                    for model in self.experiment_dict['model_components'].keys():
                        model_dict = {model: {}}
                        for question in task_questions[task].expand_question_list(model):
                            model_dict[model][question['question_name']] = question
                        
                        self.question_dictionary_model_dep = add_dict(self.question_dictionary_model_dep, model_dict)
                
                    for question in task_questions[task].expand_question_list():
                        if question['models'] is not None:
                            for model in self.experiment_dict['model_components'].keys():
                                model_dict = {model: {}}
                                for question in task_questions[task].expand_question_list(model):
                                    if model in question['models'] or 'all_models' in question['models']:
                                        model_dict[model][question['question_name']] = question

                                self.question_dictionary_model_dep = add_dict(self.question_dictionary_model_dep, model_dict)
                
                else:
                    question_dict = {}
                    for question in task_questions[task].expand_question_list():
                        if question['models'] is not None:
                            self.logger.abort('The model components question has not been answered.')
                        else:
                            question_dict[question['question_name']] = question

                    self.question_dictionary_model_ind = add_dict(self.question_dictionary_model_ind, question_dict)

    def prepare_suite_question_dictionary(self) -> None:

        question_dictionary_model_ind = {}
        question_dictionary_model_dep = {}

        suite_config_obj = SuiteConfigs.get_config(self.suite_config)
        suite_question_list = suite_config_obj.expand_question_list()

        for model in self.possible_model_components:
            question_dictionary_model_dep[model] = {}

            for question in suite_config_obj.expand_question_list(model):
                question_dictionary_model_dep[model][question['question_name']] = question

        for question in suite_question_list:
            if question['models'] is None:
                question_dictionary_model_ind[question['question_name']] = question
            else:
                if 'all_models' in question['models']:
                    question_models = self.possible_model_components
                else:
                    question_models = question['models']

                for model in question_models:
                    question_dictionary_model_dep = add_dict(question_dictionary_model_dep, {model: {question['question_name']: question}})

        self.suite_needs_model_components = True
        if 'model_components' not in question_dictionary_model_ind.keys():
            self.suite_needs_model_components = False

        self.question_dictionary_model_ind = question_dictionary_model_ind
        self.question_dictionary_model_dep = question_dictionary_model_dep

    def override_with_defaults(self, suite_task: QuestionType) -> None:

        # Perform a platform override on the model_ind dictionary
        # -------------------------------------------------------
        platform_defaults = {}

        platform_dict_file = os.path.join(get_swell_path(), 'deployment', 'platforms',
                                          self.platform, f'{suite_task.value}_questions.yaml')
        with open(platform_dict_file, 'r') as ymlfile:
            platform_defaults.update(yaml.safe_load(ymlfile))

        # Loop over the keys in self.question_dictionary_model_ind and update with platform_defaults
        # if that dictionary shares the key
        for question_name, question in self.question_dictionary_model_ind.items():
            if question['question_type'] == suite_task:
                if question_name in platform_defaults.keys():
                    for key, val in platform_defaults[question_name].items():
                        if key not in question.keys() or question[key] == 'defer_to_platform':
                            question[key] = val
                        
        # Perform a model override on the model_dep dictionary
        # ----------------------------------------------------
        if self.suite_needs_model_components:
            for model, model_dict in self.question_dictionary_model_dep.items():

                # Open the suite and task default dictionaries
                model_defaults = {}
                
                model_dict_file = os.path.join(get_swell_path(), 'configuration', 'jedi',
                                               'interfaces', model, f'{suite_task.value}_questions.yaml')
                with open(model_dict_file, 'r') as ymlfile:
                    model_defaults.update(yaml.safe_load(ymlfile))

                # Loop over the keys in self.question_dictionary_model_ind and update with
                # model_defaults or platform_defaults if that dictionary shares the key
                for question_name, question in model_dict.items():
                    if question['question_type'] == suite_task:
                        if question_name in model_defaults.keys():
                            for key, val in question.items():
                                # If the value of the question is still set as model-dependent,
                                # set the value for that model
                                if isinstance(val, Mapping) and \
                                    'depends_on_model' in val.keys() and \
                                    model in val['depends_on_model'].keys() and \
                                    val['depends_on_model'][model] != 'defer_to_model':

                                    model_dict[question_name][key] = val['depends_on_model'][model]
                                elif key in model_defaults[question_name].keys() and (
                                        val == 'defer_to_model' or val is None):
                                    model_dict[question_name][key] = model_defaults[question_name][key]

                        if question_name in platform_defaults.keys():
                            for key, val in platform_defaults[question_name].items():
                                if val == 'defer_to_platform':
                                    model_dict[question_name][key] = platform_defaults[
                                        question_name][key]

        # Look for defer_to_code in the model_ind dictionary
        # --------------------------------------------------
        for question_name, question in self.question_dictionary_model_ind.items():
            if question['question_type'] == suite_task:
                if question_name == 'model_components':
                    if question['default_value'] == 'defer_to_code':
                        question['default_value'] = self.possible_model_components
                    if question['options'] == 'defer_to_code':
                        question['options'] = self.possible_model_components

                if question_name == 'experiment_id' and question['default_value'] == 'defer_to_code':
                    question['default_value'] = f'swell-{self.suite}'

    # ----------------------------------------------------------------------------------------------

    def override_with_external(self, suite_task: QuestionType) -> None:

        # Append with any user provide overrides
        if self.override is not None:

            # Create an override dictionary
            override_dict = {}

            if isinstance(self.override, Mapping):
                override_dict.update_dict(override_dict, self.override)

            elif isinstance(self.override, str):
                with open(self.override, 'r') as ymlfile:
                    override_dict = update_dict(override_dict, yaml.safe_load(ymlfile))
            else:
                self.logger.abort(f'Override must be a dictionary or a path to a yaml file.')

            # In this case the user is sending in a dictionary that looks like the experiment
            # dictionary that they will ultimately be looking at. This means the dictionary does
            # not contain default_value or options and the override cannot be performed.

            # Iterate over the model_ind dictionary and override
            # --------------------------------------------------
            for question_name, question in self.question_dictionary_model_ind.items():
                if question['question_type'] == suite_task:
                    if question_name in override_dict:
                        question['default_value'] = override_dict[question_name]

            # Iterate over the model_dep dictionary and override
            # --------------------------------------------------
            if self.suite_needs_model_components and override_dict['models'] is not None:
                for model, model_dict in self.question_dictionary_model_dep.items():
                    for question_name, question in model_dict.items():
                        if question['question_type'] == suite_task:
                            if model in override_dict['models']:
                                if question_name in override_dict['models'][model]:
                                    question['default_value'] = override_dict['models'][model][question_name]

    # ----------------------------------------------------------------------------------------------

    def get_questions_of_type(self, suite_task: QuestionType, question_dictionary: Mapping) -> Mapping:
        out_dict = {}
        
        if 'models' in question_dictionary.keys():
            for model in self.possible_model_components:
                if model in question_dictionary.keys():
                    out_dict[model] = self.get_questions_of_type(suite_task, question_dictionary[model])

        else:
            for question_name, question in question_dictionary.items():
                if question['question_type'] == suite_task:
                    out_dict[question['question_name']] = question
        
        return out_dict

    # ----------------------------------------------------------------------------------------------

    def ask_questions_and_configure(self, suite_task: QuestionType) -> Tuple[dict, dict]:

        if self.config_client.__class__.__name__ == 'GetAnswerCli' and suite_task == QuestionType.SUITE:
            self.logger.info("Please answer the following questions to configure your experiment ")

        for question_name, question in self.get_questions_of_type(suite_task, self.question_dictionary_model_ind).items():
            self.ask_a_question(self.question_dictionary_model_ind, question_name)

        if self.suite_needs_model_components:
            if 'model_components' not in self.experiment_dict:
                self.logger.abort('The model components question has not been answered.')

            for model in self.experiment_dict['model_components']:
                model_dict = self.question_dictionary_model_dep[model]

                for question_name, question in self.get_questions_of_type(suite_task, model_dict).items():
                    self.ask_a_question(model_dict, question_name, model)

    # ----------------------------------------------------------------------------------------------
    def ask_a_question(
        self,
        full_question_dictionary: dict,
        question_key: str,
        model: Optional[str] = None
    ) -> None:

        # Set flag for whether the question should be asked
        ask_question = self.question_not_been_asked(question_key, model)

        qd = full_question_dictionary[question_key]

        # If model is not none then ensure the experiment dictionary has a dictionary for the model
        if model is not None:
            if 'models' not in self.experiment_dict:
                self.experiment_dict['models'] = {}
                self.comment_dict['models'] = f"Configurations for the model components."
            if model not in self.experiment_dict['models']:
                self.experiment_dict['models'][model] = {}
                self.comment_dict[f'models.{model}'] = \
                    f"Configuration for the {model} model component."

        # Check the dependency chain for the question
        if dict_get(self.logger, qd, 'depends', None) is not None:
            for key, val in qd['depends'].items():

                # Check is dependency has been asked
                if self.question_not_been_asked(key, model):

                    # Iteratively ask the dependent question
                    self.ask_a_question(full_question_dictionary, key, model)

                # Check that answer for dependency matches the required value
                if model is None:
                    if self.experiment_dict[key] != val:
                        ask_question = False
                else:
                    prev = self.experiment_dict['models'][model][key]
                    if prev != val:
                        ask_question = False

        # Ask the question using the selected client
        if ask_question:
            if model is None:
                self.experiment_dict[question_key] = self.config_client.get_answer(
                        self.logger, question_key, qd)
                self.questions_dict[question_key] = qd['prompt']
            else:
                self.experiment_dict['models'][model][question_key] = \
                    self.config_client.get_answer(self.logger, question_key, qd, model)
                self.questions_dict[f'models.{model}.{question_key}'] = qd['prompt']

    # ----------------------------------------------------------------------------------------------

    def question_not_been_asked(self, question_key: str, model: str) -> bool:
        # See if a question has been answered in the experiment dict

        # Check model independent keys
        if model is None and question_key in self.experiment_dict:
            return False
        # Check model dependent keys in the specific model
        elif 'models' in self.experiment_dict and model in self.experiment_dict['models'] and (
                question_key in self.experiment_dict['models'][model]):
            return False

        return True

    # ----------------------------------------------------------------------------------------------

    def get_suite_task_list_model_ind(self, suite_str: str) -> list:

        # Search the suite string for lines containing 'swell task' and not '-m'
        swell_task_lines = [line for line in suite_str.split('\n') if 'swell task' in line and
                            '-m' not in line]

        # Now get the task part
        tasks = []
        for line in swell_task_lines:
            # Split by 'swell task'
            # Remove any leading spaces
            # Split by space
            tasks.append(line.split('swell task')[1].strip().split(' ')[0])

        # Ensure there are no duplicate tasks
        tasks = list(set(tasks))

        # Return tasks
        return tasks

    # ----------------------------------------------------------------------------------------------

    def get_all_model_dep_tasks(self, suite_str: str) -> list:

        # Search the suite string for lines containing 'swell task' and '-m'
        swell_task_lines = [line for line in suite_str.split('\n') if 'swell task' in line and
                            '-m' in line]

        # Strip " and spaces from all lines
        swell_task_lines = [line.replace('"', '') for line in swell_task_lines]
        swell_task_lines = [line.strip() for line in swell_task_lines]

        # All tasks
        all_tasks = []

        for line in swell_task_lines:
            all_tasks.append(line.split('swell task ')[1].split(' ')[0])

        # Ensure all_tasks are unique
        all_tasks = list(set(all_tasks))

        return all_tasks

    # ----------------------------------------------------------------------------------------------

    def get_suite_task_list_model_dep(self, suite_str: str) -> dict:

        # Search the suite string for lines containing 'swell task' and '-m'
        swell_task_lines = [line for line in suite_str.split('\n') if 'swell task' in line and
                            '-m' in line]

        # Strip " and spaces from all lines
        swell_task_lines = [line.replace('"', '') for line in swell_task_lines]
        swell_task_lines = [line.strip() for line in swell_task_lines]

        # Now get the model part
        models = []
        for line in swell_task_lines:
            models.append(line.split('-m')[1].split('0')[0].strip())

        # Unique models
        models = list(set(models))

        # Assemble dictionary where key is model and val is the tasks that model is associated with
        model_tasks = {}
        for model in models:

            # Get all elements of swell_task_lines that contains "-m {model}"
            model_tasks_this_model = [line for line in swell_task_lines if f'-m {model}' in line]

            # Get task name
            tasks = []
            for line in model_tasks_this_model:
                tasks.append(line.split('swell task ')[1].split(' ')[0])

            # Unique model tasks
            model_tasks[model] = list(set(tasks))

        # Return the dictionary
        return model_tasks

    # ----------------------------------------------------------------------------------------------

    def get_dynamic_tasks(self, question_list: list) -> list:
        tasks = []

        for question in question_list:
            if question['question_name'] == 'dynamic_task_list':
                tasks.extend(question['default_value'])

        return tasks

# --------------------------------------------------------------------------------------------------
