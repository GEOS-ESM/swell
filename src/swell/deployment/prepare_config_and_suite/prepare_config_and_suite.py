# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import copy
import os
import yaml
from typing import Union, Tuple, Optional

from swell.swell_path import get_swell_path
from swell.deployment.prepare_config_and_suite.question_and_answer_cli import GetAnswerCli
from swell.deployment.prepare_config_and_suite.question_and_answer_defaults import GetAnswerDefaults
from swell.utilities.logger import Logger
from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.dictionary import update_dict


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
        platform: str,
        config_client: str,
        override: Union[str, dict, None]
    ) -> None:

        # Store local copy of the inputs
        self.logger = logger
        self.suite = suite
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
        self.questions_dict = {}

        # Get list of all possible models
        self.possible_model_components = os.listdir(os.path.join(get_swell_path(), 'configuration',
                                                                 'jedi', 'interfaces'))

        # Read suite file into a string
        suite_file = os.path.join(get_swell_path(), 'suites', self.suite, 'flow.cylc')
        with open(suite_file, 'r') as suite_file_open:
            self.suite_str = suite_file_open.read()

        # Perform the assembly of the dictionaries that contain all the questions that can possibly
        # be asked. This
        self.prepare_question_dictionaries()
        self.override_with_defaults()
        self.override_with_external()

    # ----------------------------------------------------------------------------------------------

    def prepare_question_dictionaries(self) -> None:

        """
        Read the suite and task question YAML files and perform various steps:

        1. Read suite and task dictionaries into a single dictionary
        2. Discard questions not associated with this suite
        3. Split the dictionary into model independent and model dependent dictionaries
        4. Create a dictionary for each possible model component

        At the end there will be two dictionaries that look like this (in YAML format):

        self.question_dictionary_model_ind:
        question1:
          ask_question: True
          default_value: 'defer_to_<something>'
          prompt: ...

        self.question_dictionary_model_dep:
          model1:
            question1:
            ask_question: True
            default_value: 'defer_to_<something>'
            prompt: ...
          model2:
            question1:
            ask_question: True
            default_value: 'defer_to_<something>'
            prompt: ...
        """

        # Read suite questions into a dictionary
        suite_questions_file = os.path.join(get_swell_path(), 'suites', 'suite_questions.yaml')
        with open(suite_questions_file, 'r') as ymlfile:
            question_dictionary = yaml.safe_load(ymlfile)

        # Read task questions into a dictionary
        task_questions_file = os.path.join(get_swell_path(), 'tasks', 'task_questions.yaml')
        with open(task_questions_file, 'r') as ymlfile:
            question_dictionary_tasks = yaml.safe_load(ymlfile)

        # Loop through question_dictionary_tasks. If the key does not already exist add to the
        # question_dictionary. If the key does exist then only add the tasks key to the existing
        # question_dictionary
        for key, val in question_dictionary_tasks.items():
            if key not in question_dictionary.keys():
                question_dictionary[key] = val
            else:
                # In this case the question is both a suite question and a task question.
                # To avoid any confusion, only the tasks key is taken from the task dictionary
                question_dictionary[key]['tasks'] = val['tasks']

        # Iterate over the question_dictionary dictionary and remove keys not associated with this
        # suite. Note that there might be questions that are not needed by the suite but could still
        # be needed by the tasks in the suite. These are not removed but the suite key is removed.
        # Note also that at this point we do not know which tasks will actually be needed so we
        # can only remove questions that are known not to be needed by the suite.
        keys_to_remove = []
        for key, val in question_dictionary.items():
            if 'suites' in val:
                # If this suite question needed then skip to the next question
                if val['suites'] == ['all'] or self.suite in val['suites']:
                    continue
                else:
                    if 'tasks' not in val:
                        # Question not needed by suite and not a task question: remove
                        keys_to_remove.append(key)
                    else:
                        # Question not needed by suite but might be needed by tasks.
                        # Reduce to a task only question.
                        val.pop('suites')
        for key in keys_to_remove:
            del question_dictionary[key]

        # At this point we can check to see if this is a suite that requires model components
        self.suite_needs_model_components = True
        if 'model_components' not in question_dictionary.keys():
            self.suite_needs_model_components = False

        # Create copy of the question_dictionary for model independent questions
        question_dictionary_model_ind = copy.deepcopy(question_dictionary)

        # Iterate through the model_ind dictionary and remove questions associated with models
        # and questions not required by the suite
        keys_to_remove = []
        for key, val in question_dictionary_model_ind.items():
            if 'models' in val.keys():
                keys_to_remove.append(key)

        # Cycle times can be a special case that is needed even when models are not. Though if they
        # are then the cycle times are needed for each model component. So we need to check if the
        # suite needs cycle_times

        # If there are no models and the cycle_times is in the keys to remove then remove it
        if not self.suite_needs_model_components and 'cycle_times' in keys_to_remove:
            keys_to_remove.remove('cycle_times')

        # Now remove the keys
        for key in keys_to_remove:
            del question_dictionary_model_ind[key]
        self.question_dictionary_model_ind = copy.deepcopy(question_dictionary_model_ind)

        # If there are no models and the cycle_times is in the keys then remove the models key from
        # the cycle_times question dictionary
        if 'cycle_times' in self.question_dictionary_model_ind.keys():
            if not self.suite_needs_model_components:
                self.question_dictionary_model_ind['cycle_times'].pop('models')
                self.question_dictionary_model_ind['cycle_times']['default_value'] = 'T00'

        # At this point we can return if there are no model components
        if not self.suite_needs_model_components:
            return

        # Create copy of the question_dictionary for model dependent questions
        question_dictionary_model_dep = copy.deepcopy(question_dictionary)

        # Iterate through the model_dep dictionary and remove questions not associated with models
        # and questions not required by the suite
        keys_to_remove = []
        for key, val in question_dictionary_model_dep.items():
            if 'models' not in val.keys():
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del question_dictionary_model_dep[key]

        # Create new questions dictionary for each model component
        self.question_dictionary_model_dep = {}
        for model in self.possible_model_components:
            self.question_dictionary_model_dep[model] = copy.deepcopy(question_dictionary_model_dep)

        # Remove any questions that are not associated with the model component
        for model in self.possible_model_components:
            keys_to_remove = []
            for key, val in self.question_dictionary_model_dep[model].items():
                if val['models'] != ['all'] and model not in val['models']:
                    keys_to_remove.append(key)  # Remove if not needed by this model

            for key in keys_to_remove:
                del self.question_dictionary_model_dep[model][key]

    # ----------------------------------------------------------------------------------------------

    def override_with_defaults(self) -> None:

        # Perform a platform override on the model_ind dictionary
        # -------------------------------------------------------
        platform_defaults = {}
        for suite_task in ['suite', 'task']:
            platform_dict_file = os.path.join(get_swell_path(), 'deployment', 'platforms',
                                              self.platform, f'{suite_task}_questions.yaml')
            with open(platform_dict_file, 'r') as ymlfile:
                platform_defaults.update(yaml.safe_load(ymlfile))

        # Loop over the keys in self.question_dictionary_model_ind and update with platform_defaults
        # if that dictionary shares the key
        for key, val in self.question_dictionary_model_ind.items():
            if key in platform_defaults.keys():
                self.question_dictionary_model_ind[key].update(platform_defaults[key])

        # Perform a model override on the model_dep dictionary
        # ----------------------------------------------------
        if self.suite_needs_model_components:
            for model, model_dict in self.question_dictionary_model_dep.items():

                # Open the suite and task default dictionaries
                model_defaults = {}
                for suite_task in ['suite', 'task']:
                    model_dict_file = os.path.join(get_swell_path(), 'configuration', 'jedi',
                                                   'interfaces', model,
                                                   f'{suite_task}_questions.yaml')
                    with open(model_dict_file, 'r') as ymlfile:
                        model_defaults.update(yaml.safe_load(ymlfile))

                # Loop over the keys in self.question_dictionary_model_ind and update with
                # model_defaults or platform_defaults if that dictionary shares the key
                for key, val in model_dict.items():
                    if key in model_defaults.keys():
                        model_dict[key].update(model_defaults[key])

                    if key in platform_defaults.keys():
                        model_dict[key].update(platform_defaults[key])

        # Look for defer_to_code in the model_ind dictionary
        # --------------------------------------------------
        for key, val in self.question_dictionary_model_ind.items():
            if val['default_value'] == 'defer_to_code':

                if key == 'experiment_id':
                    val['default_value'] = f'swell-{self.suite}'

                if key == 'model_components':
                    val['default_value'] = self.possible_model_components
                    val['options'] = self.possible_model_components

    # ----------------------------------------------------------------------------------------------

    def override_with_external(self) -> None:

        # Create and override dictionary
        override_dict = {}

        # Always start the override with the a suite test file
        test_file = os.path.join(get_swell_path(), 'test', 'suite_tests',
                                 self.suite + '-tier1.yaml')
        if os.path.exists(test_file):
            with open(test_file, 'r') as ymlfile:
                override_dict = yaml.safe_load(ymlfile)

        # Update overrides with tier2 suite test file if available
        tier2_test_file = os.path.join(get_swell_path(), 'test', 'suite_tests',
                                       self.suite + '-tier2.yaml')
        if os.path.exists(tier2_test_file):
            with open(tier2_test_file, 'r') as ymlfile:
                tier2_override_dict = yaml.safe_load(ymlfile)
            override_dict = update_dict(override_dict, tier2_override_dict)

        # Now append with any user provided override
        if self.override is not None:

            if isinstance(self.override, dict):
                override_dict.update(self.override)
            elif isinstance(self.override, str):
                with open(self.override, 'r') as ymlfile:
                    override_dict.update(yaml.safe_load(ymlfile))
            else:
                self.logger.abort(f'Override must be a dictionary or a path to a yaml file.')

        # In this case the user is sending in a dictionary that looks like the experiment dictionary
        # that they will ultimately be looking at. This means the dictionary does not contain
        # default_value or options and the override cannot be performed.

        # Iterate over the model_ind dictionary and override
        # --------------------------------------------------
        for key, val in self.question_dictionary_model_ind.items():
            if key in override_dict:
                val['default_value'] = override_dict[key]

        # Iterate over the model_dep dictionary and override
        # --------------------------------------------------
        if self.suite_needs_model_components:
            for model, model_dict in self.question_dictionary_model_dep.items():
                for key, val in model_dict.items():
                    if model in override_dict['models']:
                        if key in override_dict['models'][model]:
                            val['default_value'] = override_dict['models'][model][key]

    # ----------------------------------------------------------------------------------------------

    def ask_questions_and_configure_suite(self) -> Tuple[dict, dict]:

        """
        This is where we ask all the questions and as we go configure the suite file. The process
        is rather complex and proceeds as described below. The order is determined by what makes
        sense to a user that is going through answering questions. For example we want them to be
        able to answer all the questions associated with a certain model together. While there is
        work going on behind the scenes to configure the suite file the user should not see a break
        in the questioning or a back and forth that causes confusion.

        1. Ask the model independent suite questions.

        2. Perform a non-exhaustive resolving of suite file templates. Non-exhaustive because at
           this point we have not asked the model dependent suite questions so there may be more
           templates to resolve.

        3. Get a list of tasks that do not depend on the model component.

        4. Ask the model independent task questions.

        5. Check that the suite in question has model_components

        6. Ask the model dependent suite questions.

        7. Perform an exhaustive resolving of suite file templates. Now it is exhaustive because at
           this point we should have all the required information to resolve all the templates.

        8. Build a list of tasks for each model component.

        9. Ask the model dependent task questions.
        """

        # If the client is CLI put out some information about what is due to happen next
        if self.config_client.__class__.__name__ == 'GetAnswerCli':
            self.logger.info("Please answer the following questions to configure your experiment ")

        # 1. Iterate over the model_ind dictionary and ask questions
        # ----------------------------------------------------------
        for question_key in self.question_dictionary_model_ind:

            # Ask only the suite questions first
            # ----------------------------------
            if 'suites' in self.question_dictionary_model_ind[question_key]:

                # Ask the question
                self.ask_a_question(self.question_dictionary_model_ind, question_key)

        # 2. Perform a non-exhaustive resolving of suite file templates
        # -------------------------------------------------------------
        suite_str = template_string_jinja2(self.logger, self.suite_str, self.experiment_dict, True)

        # 3. Get a list of tasks that do not depend on the model component
        # ----------------------------------------------------------------
        model_ind_tasks = self.get_suite_task_list_model_ind(suite_str)

        # 4.1 Iterate over the model_ind dictionary and ask task questions
        # ----------------------------------------------------------------
        for question_key in self.question_dictionary_model_ind:

            # Ask the task questions
            # ----------------------
            if 'suites' not in self.question_dictionary_model_ind[question_key]:

                # Get list of tasks for the question
                question_tasks = self.question_dictionary_model_ind[question_key]['tasks']

                # Check whether any of model_ind_tasks are in question_tasks
                if any(elem in question_tasks for elem in model_ind_tasks):

                    # Ask the question
                    self.ask_a_question(self.question_dictionary_model_ind, question_key)

        # 5. Check that the suite in question has model_components
        # --------------------------------------------------------
        if not self.suite_needs_model_components:
            return self.experiment_dict, self.questions_dict

        # 6. Iterate over the model_dep dictionary and ask suite questions
        # ----------------------------------------------------------------

        # At this point the user should have provided the model components answer. Check that it is
        # in the experiment dictionary and retrieve the response
        if 'model_components' not in self.experiment_dict:
            self.logger.abort('The model components question has not been answered.')

        for model in self.experiment_dict['model_components']:

            model_dict = self.question_dictionary_model_dep[model]

            # Loop over keys of each model
            for question_key in model_dict:

                # Ask only the suite questions first
                if 'suites' in model_dict[question_key]:

                    # Ask the question
                    self.ask_a_question(model_dict, question_key, model)

        # 7. Perform a more exhaustive resolving of suite file templates
        # --------------------------------------------------------------
        # Note that we reset the suite file to avoid templates having been left unresolved
        # (removed) from the previous attempt. We still do not ask for an exhaustive resolving
        # of templates because there are things related to scheduling that are not yet able to be
        # resolved. In the future it might be good to bring some of that information into the
        # sphere of suite questions but that requires some careful thought so as not to overload
        # the user with questions.
        suite_str = template_string_jinja2(self.logger, self.suite_str, self.experiment_dict,
                                           True)

        # 8. Build a list of tasks for each model component
        # -------------------------------------------------
        model_dep_tasks, all_tasks = self.get_suite_task_list_model_dep(suite_str)

        # 9.1 Ask the new task questions that do not actually depend on the model
        # -----------------------------------------------------------------------
        for question_key in self.question_dictionary_model_ind:

            if 'tasks' in self.question_dictionary_model_ind[question_key]:

                # Get list of tasks for the question
                question_tasks = self.question_dictionary_model_ind[question_key]['tasks']

                # Check whether any of model_dep_tasks are in question_tasks
                if any(elem in question_tasks for elem in all_tasks):

                    # Ask the question
                    self.ask_a_question(self.question_dictionary_model_ind, question_key)

        # 9.2 Iterate over the model_dep dictionary and ask task questions
        # ----------------------------------------------------------------
        for model in self.experiment_dict['model_components']:

            # Iterate over the model_dep dictionary and ask questions
            # -------------------------------------------------------
            for question_key in self.question_dictionary_model_dep[model]:

                # Ask only the task questions first
                # ----------------------------------
                if 'suites' not in self.question_dictionary_model_dep[model][question_key]:

                    # Get list of tasks for the question
                    question_tasks = \
                        self.question_dictionary_model_dep[model][question_key]['tasks']

                    # Check whether any of model_dep_tasks are in question_tasks
                    if any(elem in question_tasks for elem in model_dep_tasks[model]):

                        # Ask the question
                        self.ask_a_question(self.question_dictionary_model_dep[model], question_key,
                                            model)

        # Return the main experiment dictionary
        return self.experiment_dict, self.questions_dict

    # ----------------------------------------------------------------------------------------------
    def ask_a_question(
        self,
        full_question_dictionary: dict,
        question_key: str,
        model: Optional[str] = None
    ) -> None:

        # Set flag for whether the question should be asked
        ask_question = True

        # Has the question already been asked?
        if question_key in self.experiment_dict:
            ask_question = False

        # Dictionary for this question
        qd = full_question_dictionary[question_key]

        # If model is not none then ensure the experiment dictionary has a dictionary for the model
        if model is not None:
            if 'models' not in self.experiment_dict:
                self.experiment_dict['models'] = {}
                self.questions_dict['models'] = f"Configurations for the model components."
            if model not in self.experiment_dict['models']:
                self.experiment_dict['models'][model] = {}
                self.questions_dict[f'models.{model}'] = \
                    f"Configuration for the {model} model component."

        # Check the dependency chain for the question
        if 'depends' in qd:

            # Check is dependency has been asked
            if qd['depends']['key'] not in self.experiment_dict:

                # Iteratively ask the dependent question
                self.ask_a_question(full_question_dictionary, qd['depends']['key'], model)

            # Check that answer for dependency matches the required value
            if model is None:
                if self.experiment_dict[qd['depends']['key']] != qd['depends']['value']:
                    ask_question = False
            else:
                prev = self.experiment_dict['models'][model][qd['depends']['key']]
                if prev != qd['depends']['value']:
                    ask_question = False

        # Ask the question using the selected client
        if ask_question:
            if model is None:
                self.experiment_dict[question_key] = self.config_client.get_answer(question_key, qd)
                self.questions_dict[question_key] = qd['prompt']
            else:
                self.experiment_dict['models'][model][question_key] = \
                    self.config_client.get_answer(question_key, qd)
                self.questions_dict[f'models.{model}.{question_key}'] = qd['prompt']

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

    def get_suite_task_list_model_dep(self, suite_str: str) -> Tuple[dict, list]:

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

        # All tasks
        all_tasks = []

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

            # Also append all tasks
            all_tasks += tasks

        # Ensure all_tasks are unique
        all_tasks = list(set(all_tasks))

        # Return the dictionary
        return model_tasks, all_tasks

# --------------------------------------------------------------------------------------------------
