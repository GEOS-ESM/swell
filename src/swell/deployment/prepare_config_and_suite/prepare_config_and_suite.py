# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import copy
import os
import yaml

from swell.swell_path import get_swell_path
from swell.deployment.prepare_config_and_suite.question_and_answer_cli import GetAnswerCli
from swell.deployment.prepare_config_and_suite.question_and_answer_defaults import GetAnswerDefaults
from swell.utilities.jinja2 import template_string_jinja2


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
   model will be

3. All the
"""


# --------------------------------------------------------------------------------------------------


class PrepareExperimentConfigAndSuite:

    # ----------------------------------------------------------------------------------------------

    def __init__(self, logger, suite, platform, config_client, override, advanced):

        # Store local copy of the inputs
        self.logger = logger
        self.suite = suite
        self.platform = platform
        self.override = override
        self.advanced = advanced

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

    def prepare_question_dictionaries(self):

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

        # Iterate over the suite_questions dictionary and remove keys not associated with this suite
        for key, val in question_dictionary.items():
            if 'suites' in val and self.suite not in val['suites']:
                del question_dictionary[key]

        # Read task questions into a dictionary
        task_questions_file = os.path.join(get_swell_path(), 'tasks', 'task_questions.yaml')
        with open(task_questions_file, 'r') as ymlfile:
            question_dictionary.update(yaml.safe_load(ymlfile))

        # Create copies that will be the task question that do and do not depend on the choice of
        # model component
        question_dictionary_model_ind = copy.deepcopy(question_dictionary)
        question_dictionary_model_dep = copy.deepcopy(question_dictionary)

        # Iterate through the model_ind dictionary and remove questions associated with models
        # and questions not required by the suite
        for key, val in question_dictionary_model_ind.items():
            if 'models' in val.keys():
                del question_dictionary_model_ind[key]

        self.question_dictionary_model_ind = copy.deepcopy(question_dictionary_model_ind)

        # Iterate through the model_dep dictionary and remove questions not associated with models
        # and questions not required by the suite
        for key, val in question_dictionary_model_dep.items():
            if 'models' not in val.keys():
                del question_dictionary_model_dep[key]

        # Create new questions dictionary for each model component
        self.question_dictionary_model_dep = {}
        for model in model_components:
            self.question_dictionary_model_dep[model] = copy.deepcopy(question_dictionary_model_dep)

    # ----------------------------------------------------------------------------------------------

    def override_with_defaults(self):

        # Perform a platform override on the model_ind dictionary
        # -------------------------------------------------------
        platform_defaults = {}
        for suite_task in ['suite', 'task']:
            platform_dict_file = os.path.join(get_swell_path(), 'deployment', 'platforms',
                                              self.platform, f'{suite_task}_questions.yaml')
            with open(platform_dict_file, 'r') as ymlfile:
                platform_defaults.update(yaml.safe_load(ymlfile))

        # Update the model_ind dictionary with platform
        self.question_dictionary_model_ind.update(platform_defaults)


        # Perform a model override on the model_dep dictionary
        # ----------------------------------------------------
        for model, model_dict in self.question_dictionary_model_dep.items():

            # Open the suite and task default dictionaries
            model_defaults = {}
            for suite_task in ['suite', 'task']:
                model_dict_file = os.path.join(get_swell_path(), 'configuration', 'jedi',
                                               'interfaces', model, f'{suite_task}_questions.yaml')
                with open(model_dict_file, 'r') as ymlfile:
                    model_defaults.update(yaml.safe_load(ymlfile))

            # Iterate and replace defer_to_model
            model_dict.update(model_defaults)


        # Look for defer_to_code in the model_ind dictionary
        # --------------------------------------------------
        for key, val in self.question_dictionary_model_ind.items():
            if 'defer_to_code' in val['default_value']:

                if key == 'experiment_id':
                    val['default_value'] = f'swell-{self.suite}'

                if key == 'model_components':
                    val['default_value'] = self.possible_model_components
                    val['options'] = self.possible_model_components

    # ----------------------------------------------------------------------------------------------

    def override_with_external(self):

        # Create and override dictionary
        override_dict = {}

        # Always start the override with the a suite test file
        test_file = os.path.join(swell_path, 'test', 'suite_tests', self.suite + '-tier1.yaml')
        if os.path.exists(test_file):
            with open(test_file, 'r') as ymlfile:
                override_dict = yaml.safe_load(ymlfile)

        # Now append with any user provided override
        if self.override is not None:

            if isinstance(self.override, dict):
                override_dict.update(self.override)
            elif isinstance(self.override, str):
                with open(self.override, 'r') as ymlfile:
                    override_dict.update(yaml.safe_load(ymlfile))
            else:
                self.logger.abort(f'Override must be a dictionary or a path to a yaml file. ' +
                                  f'Instead it is {type(override)}')

        # In this case the user is sending in a dictionary that looks like the experiment dictionary
        # that they will ultimately be looking at. This means the dictionary does not contain
        # default_value or options and the override cannot be performed.

        # Iterate over the model_ind dictionary and override
        # --------------------------------------------------
        for key, val in self.question_dictionary_model_ind.items():
            if key in override_dict.keys():
                val['default_value'] = override_dict[key]

        # Iterate over the model_dep dictionary and override
        # --------------------------------------------------
        for model, model_dict in self.question_dictionary_model_dep.items():
            for key, val in model_dict.items():
                if key in override_dict[model].keys():
                    val['default_value'] = override_dict[model][key]

    # ----------------------------------------------------------------------------------------------

    def ask_questions_and_configure_suite(self):

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
        if type(self).__name__.split('PrepConfig')[1] == 'Cli':
            self.logger.info("Please answer the following questions to configure your experiment ")

        # 1. Iterate over the model_ind dictionary and ask questions
        # ----------------------------------------------------------
        for question_key in self.question_dictionary_model_ind.keys():

            # Ask only the suite questions first
            # ----------------------------------
            if 'suites' in self.question_dictionary_model_ind[question_key].keys():

                # Ask the question
                self.ask_a_question(self.question_dictionary_model_ind, question_key)

        # 2. Perform a non-exhaustive resolving of suite file templates
        # -------------------------------------------------------------
        self.suite_str = template_string_jinja2(self.suite_str, self.experiment_dict, True)

        # 3. Get a list of tasks that do not depend on the model component
        # ----------------------------------------------------------------
        model_ind_tasks = self.get_suite_task_list_model_ind()

        # 4. Iterate over the model_ind dictionary and ask task questions
        # ---------------------------------------------------------------
        for question_key in self.question_dictionary_model_ind.keys():

            # Ask only the suite questions first
            # ----------------------------------
            if 'suites' not in self.question_dictionary_model_ind[question_key].keys():

                # Get list of tasks for the question
                question_tasks = self.question_dictionary_model_ind[question_key]['tasks']

                # Check whether any of model_ind_tasks are in question_tasks
                if any(elem in question_tasks for elem in model_ind_tasks):

                    # Ask the question
                    self.ask_a_question(self.question_dictionary_model_ind, question_key)

        # 5. Check that the suite in question has model_components
        # --------------------------------------------------------
        if 'model_components' not in self.experiment_dict.keys():
            return

        # 6. Iterate over the model_dep dictionary and ask suite questions
        # ----------------------------------------------------------------
        for question_key in self.question_dictionary_model_dep.keys():

            # Ask only the suite questions first
            # ----------------------------------
            if 'suites' in self.question_dictionary_model_dep[question_key].keys():

                # Ask the question
                self.ask_a_question(self.question_dictionary_model_dep, question_key)

        # 7. Perform an exhaustive resolving of suite file templates
        # ----------------------------------------------------------
        self.suite_str = template_string_jinja2(self.suite_str, self.experiment_dict, False)

        # 8. Build a list of tasks for each model component
        # -------------------------------------------------
        model_dep_tasks = self.get_suite_task_list_model_dep()

        # 9. Iterate over the model_dep dictionary and ask task questions
        # ---------------------------------------------------------------
        for model in self.experiment_dict['model_components']:

            # Iterate over the model_dep dictionary and ask questions
            # -------------------------------------------------------
            for question_key in self.question_dictionary_model_dep.keys():

                # Ask only the suite questions first
                # ----------------------------------
                if 'suites' not in self.question_dictionary_model_dep[question_key].keys():

                    # Get list of tasks for the question
                    question_tasks = self.question_dictionary_model_dep[question_key]['tasks']

                    # Check whether any of model_dep_tasks are in question_tasks
                    if any(elem in question_tasks for elem in model_dep_tasks[model]):

                        # Ask the question
                        self.ask_a_question(self.question_dictionary_model_dep, question_key)


        # Return the main experiment dictionary
        return self.experiment_dict, self.question_dict, self.suite_str


    # ----------------------------------------------------------------------------------------------


    def ask_a_question(self, full_question_dictionary, question_key):

        # Set flag for whether the question should be asked
        ask_question = True

        # Has the question already been asked?
        if question_key in self.experiment_dict.keys():
            ask_question = False

        # Dictionary for this question
        qd = full_question_dictionary[question_key]

        # Check the dependency chain for the question
        if 'depends' in qd.keys():

            # Check is dependency has been asked
            if qd['depends']['key'] not in self.experiment_dict.keys():

                # Iteratively ask the dependent question
                self.ask_a_question(full_question_dictionary, qd['depends']['key'])

            # Check that answer for dependency is matches the required value
            if self.experiment_dict[qd['depends']['key']] != qd['depends']['value']:
                ask_question = False

        # Ask the question using the selected client
        if ask_question:
            self.experiment_dict[question_key] = self.config_client.get_answer(question_key, qd)
            self.question_dict[question_key] = qd['prompt']


    # ----------------------------------------------------------------------------------------------


    def get_suite_task_list_model_ind(self):

        # Search the self.suite string for lines containing 'swell task' and not '-m'
        swell_task_lines = [line for line in self.suite_str.split('\n') if 'swell task' in line and
                            '-m' not in line]

        # Now get the task part
        tasks = []
        for line in swell_task_lines:
            tasks.append(line.split('swell task')[1].split(' ')[2])

        # Ensure there are no duplicate tasks
        tasks = list(set(tasks))

        # Return tasks
        return tasks


    # ----------------------------------------------------------------------------------------------

    def get_suite_task_list_model_dep(self):

        # Search the self.suite string for lines containing 'swell task' and '-m'
        swell_task_lines = [line for line in self.suite_str.split('\n') if 'swell task' in line and
                            '-m' in line]

        # Now get the model part
        models = []
        for line in swell_task_lines:
            models.append(line.split('swell task')[1].split('-m')[1].split(' ')[0])

        # Unique models
        models = list(set(models))

        # Assemble dictionary where key is model and val is the tasks that model is associated with
        model_tasks = {}
        for model in models:

            # Get all elements of swell_task_lines that contains "-m {model}"
            model_tasks_this_model = [line for line in swell_task_lines if f'-m {model}' in line]

            # Unique model tasks
            model_tasks[model] = list(set(model_tasks_this_model))

        # Return the dictionary
        return model_tasks


# --------------------------------------------------------------------------------------------------
