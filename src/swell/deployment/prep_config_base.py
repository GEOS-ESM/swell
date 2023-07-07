# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from abc import ABC, abstractmethod
import copy
import datetime
import os
import pathlib
import re
import yaml

import glob

from swell.swell_path import get_swell_path
from swell.utilities.jinja2 import template_string_jinja2

# --------------------------------------------------------------------------------------------------


class PrepConfigBase(ABC):

    def __init__(self, logger, dictionary_file, suite, platform):

        # Store a logger for all to use
        self.logger = logger

        # Swell install path
        swell_path = get_swell_path()
        self.install_path = swell_path

        # Get the path and filename of the suite dictionary
        self.directory = os.path.join(swell_path, 'suites_new')
        self.filename = os.path.splitext(os.path.basename(dictionary_file))[0]

        # Keep track of the model, atmosphere, ocean etc
        self.model_path = os.path.join(self.install_path,
                                       'configuration',
                                       'jedi/interfaces/')
        self.model = None
        self.model_task = False
        self.default_models = ['geos_atmosphere', 'geos_ocean']
        self.selected_models = None

        # Create executable keys list
        self.exec_keys = []

        # Experiment dictionary to be created and used in swell
        self.experiment_dict = {}

        # Add cli arguments to experiment dictionary
        self.experiment_dict['suite_to_run'] = suite
        self.experiment_dict['platform'] = platform

        # Comment dictionary to be created and used to add comments to config file
        self.comment_dict = {}

        # Dictionary validation things
        self.valid_types = ['string', 'integer',
                            'iso-datetime', 'iso-duration',
                            'string-list', 'integer-list',
                            'string-drop-list', 'string-check-list',
                            'boolean']

        # Disallowed element types
        self.dis_elem_types = [datetime.datetime, datetime.date]

        # Track the suite and platform that the user may input through the prepare_config path
        self.suite_to_run = suite
        self.platform = platform

        # Open the platform specific defaults
        platform_dict_file = os.path.join(swell_path, 'deployment', 'platforms', platform,
                                          'suite_questions.yaml')
        with open(platform_dict_file, 'r') as platform_dict_file_open:
            platform_dict_str = platform_dict_file_open.read()

        # Dictionary of defaults for platform
        # Use for 'defer_to_platform' default
        self.platform_dictionary = yaml.safe_load(platform_dict_str)

        # Open Master ask questions yaml
        with open(os.path.join(swell_path, 'tasks', 'task_questions.yaml'), 'r') as ymlfile:
            self.all_task_questions = yaml.safe_load(ymlfile)

    # ----------------------------------------------------------------------------------------------

    def execute(self):
        # Open the suite_to_run selected
        # check_widgets goes in cli
        # defaults gets nothing

        print("Please answer the following questions to generate your experiment " +
              "configuration YAML file.\n")

        # Set current dictionary variable which is needed for answer changes
        self.current_dictionary = {}

        # Get answers for the suite YAML file and generate task lists
        base_tasks, model_tasks = self.suite_setup()

        # Check if users wish to change any answers
        self.before_next()

        # Open the platform specific task template and reassign platform dictionary
        platform_dict_file = os.path.join(self.install_path,
                                          'deployment',
                                          'platforms',
                                          self.platform,
                                          'task_questions.yaml')

        with open(platform_dict_file, 'r') as platform_dict_file_open:
            platform_dict_str = platform_dict_file_open.read()

        # Dictionary of defaults for platform
        # Use for 'defer_to_platform' default
        self.platform_dictionary = yaml.safe_load(platform_dict_str)

        # Iterate over main task dictionary and get answers for base tasks
        self.dictionary_comber(base_tasks)

        # Iterate over main task dictionary and get answers for model tasks
        if model_tasks:
            # Find out what model components are to be used in the config
            self.selected_models = self.get_models()
            # Create a dictionary in which each key is a selected model
            # each model key has a value equal to a dictionary of defaults
            # defaults are retrieved from task defaults in interfaces model directory
            self.get_model_defaults()
            self.model_comber(model_tasks)
        else:
            pass

        return

    # ----------------------------------------------------------------------------------------------

    def suite_setup(self):

        # Get experiment id
        key = 'experiment_id'

        val = {
                'ask_question': True,
                'default_value': f'swell-{self.suite_to_run}',
                'prompt': 'Enter the experiment ID',
                'type': 'string',
              }

        val['default_value'] = self.get_answer(key, val)

        self.add_to_experiment_dictionary(key, val)

        # Get experiment root
        key = 'experiment_root'

        val = {
                'ask_question': True,
                'default_value': 'defer_to_platform',
                'prompt': 'Enter the path where experiment will be staged',
                'type': 'string',
              }

        val = self.show_deference(key, val)

        val['default_value'] = self.get_answer(key, val)

        self.add_to_experiment_dictionary(key, val)

        # Look in suite_to_run dir and check for suite yaml file, if not, grep the flow.cylc file

        # Check which suite to run, check for suite_questions yaml, and grep flow file
        self.directory = os.path.join(self.directory, self.suite_to_run)
        suite_questions_path = os.path.join(self.directory, 'suite_questions.yaml')

        if os.path.exists(suite_questions_path):
            with open(suite_questions_path, 'r') as suite_dict_file:
                suite_questions_dict = yaml.safe_load(suite_dict_file.read())
            # Iterate over the suite questions dictionary and send to key passer
            for k, v in suite_questions_dict.items():
                if k in self.experiment_dict.keys():
                    pass
                else:
                    self.key_passer(k, v)
            self.before_next()
        else:
            pass

        # Get the tasks asked prior to model selection and model-based tasks
        base_tasks, model_tasks = self.open_flow()

        return base_tasks, model_tasks

    # ----------------------------------------------------------------------------------------------

    def show_deference(self, key, el_dict):

        if 'defer_to_' in el_dict['default_value']:
            pass
        else:
            return el_dict

        if 'defer_to_platform' == el_dict['default_value']:
            el_dict['default_value'] = self.platform_dictionary[key]['default_value']
        elif 'defer_to_model' == el_dict['default_value']:
            el_dict['default_value'] = self.model_defaults_dict[self.model][key]['default_value']
            if 'options' in self.model_defaults_dict[self.model][key].keys()\
                    and 'defer_to_model' == el_dict['options']:
                el_dict['options'] = self.model_defaults_dict[self.model][key]['options']

        return el_dict

    # ----------------------------------------------------------------------------------------------

    def key_passer(self, key, el_dict):

        # Validate the element dictionary
        self.validate_dictionary(el_dict)

        # Check that the key does not have a dependency
        depends_flag = True
        if 'depends' in el_dict.keys():
            dep_key = el_dict['depends']['key']
            dep_val = el_dict['depends']['value']
            if self.model is None:
                if self.experiment_dict[dep_key] != dep_val:
                    depends_flag = False
            else:
                if self.experiment_dict['models'][self.model][dep_key] != dep_val:
                    depends_flag = False

        # In this case the key is not expected to refer to a sub dictionary but have
        # everything needed in the elements dictionary
        if depends_flag:
            el_dict = self.show_deference(key, el_dict)
            if el_dict['ask_question']:
                el_dict['default_value'] = self.get_answer(key, el_dict)
            else:
                pass
            self.add_to_experiment_dictionary(key, el_dict)

        return

    # ----------------------------------------------------------------------------------------------

    def validate_dictionary(self, dictionary):

        # Check for required key
        required_keys = ['default_value', 'prompt', 'type']
        for required_key in required_keys:
            if required_key not in dictionary.keys():
                self.logger.abort(f'Each section of the suites config files must contain the key ' +
                                  f'\'{required_key}\'. Offending dictionary: \n {dictionary}')

        # Check that type is supported
        type = dictionary['type']
        if type not in self.valid_types:
            self.logger.abort(f'Dictionary has type \'{type}\' that is not one of the supported ' +
                              f'types: {self.valid_types}. Offending dictionary: \n {dictionary}')

    # ----------------------------------------------------------------------------------------------

    def add_to_experiment_dictionary(self, key, element_dict):

        # Add elements to the current dictionary
        # --------------------------------------
        self.current_dictionary[key] = element_dict

        # Add executed key to exec_keys list
        # ----------------------------------
        self.exec_keys.append(key)

        # Set the element
        # ---------------
        element = element_dict['default_value']
        prompt = element_dict['prompt']

        # Validate the element
        # --------------------

        # Ensure always a list to make following logic not need to check if list or not
        if not isinstance(element, list):
            element_items = [element]
        else:
            element_items = element

        # Check for disallowed element types
        for element_item in element_items:
            element_item_type = type(element_item)
            for dis_elem_type in self.dis_elem_types:
                if isinstance(element_item, dis_elem_type):
                    self.logger.abort(f'Element \'{element}\' has a type that is not permitted. ' +
                                      f'Type is \'{dis_elem_type}\'. Try replacing with a string ' +
                                      f'in the configuration file.')

        # Validate the key
        # ----------------

        # Ensure there are no spaces in the key
        if ' ' in key:
            self.logger.abort(f'Key \'{key}\' contains a space. For consistency across the ' +
                              f'configurations please avoid spaces and instead use _ if needed.')

        # Check that dictionary does not already contain the key
        if key in self.experiment_dict.keys():
            self.logger.abort(f'Key \'{key}\' is already in the experiment dictionary.')

        # Check if models key is present in experiment dictionary
        if self.model is not None:
            if 'models' not in self.experiment_dict.keys():
                self.experiment_dict['models'] = {}

            # If specific model dictionary not added to the list of model then add it
            if self.model not in self.experiment_dict['models'].keys():
                self.experiment_dict['models'][self.model] = {}

        # Make sure the element was not already added
        # -------------------------------------------
        if self.model is None:
            if key in self.experiment_dict.keys():
                self.logger.abort(f'Key \'{key}\' is already in the experiment dictionary.')
        else:
            if key in self.experiment_dict['models'][self.model].keys():
                self.logger.abort(f'Key \'{key}\' is already in the experiment dictionary.')

        # Add element
        # -----------
        if self.model is None:
            self.experiment_dict[key] = element
        else:
            self.experiment_dict['models'][self.model][key] = element

        # Add option
        # ----------
        if self.model is None:
            option_key = key
        else:
            if 'models' not in self.comment_dict.keys():
                self.comment_dict['models'] = 'Options for individual model components'
            if 'models.' + self.model not in self.comment_dict.keys():
                self.comment_dict['models.' + self.model] = f'Options for the {self.model} ' + \
                                                            f'model component'
            option_key = 'models.' + self.model + '.' + key
        self.comment_dict[option_key] = prompt

    # ----------------------------------------------------------------------------------------------

    def dictionary_comber(self, task_list):

        for t in task_list:
            self.current_dictionary = {}
            question_dict = {}
            dependent_dict = {}
            # Pass the task list to get the question dictionaries required for
            # the task. Do not get the questions that depend on prior questions
            question_dict = self.build_question_dictionary(t, get_dependents=False)
            # Get the question dictionaries that depend on previous questions
            dependent_dict = self.build_question_dictionary(t, get_dependents=True)
            # Combine the two dictionaries above
            question_dict.update(dependent_dict)
            # Loop through the task questions and ask questions that have not
            # been asked and added to the experiment dictionary
            for k, v in question_dict.items():
                if self.model is None:
                    if k in self.experiment_dict.keys():
                        continue
                else:
                    if 'models' in self.experiment_dict.keys():
                        if self.model in self.experiment_dict['models'].keys():
                            if k in self.experiment_dict['models'][self.model].keys():
                                continue
                self.key_passer(k, v)
            self.before_next()
            del question_dict
            del dependent_dict
        return

    # ----------------------------------------------------------------------------------------------

    def build_question_dictionary(self, task, get_dependents):
        question_dictionary = {}
        model_key_list = ['all'] + [self.model]
        big_dictionary = copy.deepcopy(self.all_task_questions)
        for k, v in big_dictionary.items():
            if self.model is not None:
                if 'models' in v.keys() and v['models'][0] in model_key_list:
                    pass
                else:
                    continue
            if task in v['tasks']:
                if get_dependents:
                    if 'depends' in v.keys():
                        question_dictionary[k] = v
                else:
                    if 'depends' not in v.keys():
                        question_dictionary[k] = v
        del big_dictionary
        return question_dictionary

    # ----------------------------------------------------------------------------------------------

    def open_flow(self):
        # open text file in read mode
        cylc_file = open(os.path.join(self.directory, 'flow.cylc'), "r")

        # read whole file to a string
        data = cylc_file.read()

        # close file
        cylc_file.close()

        # Find the double bracket items in the Tasks section of the flow file to ID required tasks
        task_s = data[(data.find('Tasks')):]
        task_s_lines = task_s.split('\n')

        base_task_list = []
        model_task_list = []
        for line in task_s_lines:
            if 'script = "swell_task' in line:
                task_name = line.split('"swell_task')[1].split(' ')[1]
                if '-m' in line:
                    if task_name in model_task_list:
                        continue
                    model_task_list.append(task_name)
                else:
                    if task_name in base_task_list:
                        continue
                    base_task_list.append(task_name)

        # add this to logger debug
        # print('\n Following tasks selected for configuration: \n',
        #      '\n ************ \n',
        #      base_task_list,
        #      '\n ************ \n')

        # print('\n Following model tasks selected for configuration: \n',
        #      '\n ************ \n',
        #      model_task_list,
        #      '\n ************ \n')

        return base_task_list, model_task_list

    # ----------------------------------------------------------------------------------------------

    def get_model_defaults(self):
        self.model_defaults_dict = {}
        for m in self.selected_models:
            model_dict_path = os.path.join(self.model_path, m, 'task_questions.yaml')
            with open(model_dict_path, 'r') as model_dict_file:
                model_comp_dict = yaml.safe_load(model_dict_file.read())
            self.model_defaults_dict[m] = model_comp_dict

    # ----------------------------------------------------------------------------------------------

    def model_comber(self, model_tasks):
        for m in self.selected_models:
            self.model = m
            self.dictionary_comber(model_tasks)

    # ----------------------------------------------------------------------------------------------

    def update_experiment_dictionary(self, key, new_value):
        if self.model is not None:
            self.experiment_dict['models'][self.model][key] = new_value
        else:
            self.experiment_dict[key] = new_value

    # ----------------------------------------------------------------------------------------------

    @abstractmethod
    def get_answer(self, dictionary):
        pass
        # The subclass has to implement an execute method since this is how it is called into
        # action.

# --------------------------------------------------------------------------------------------------


def camel_to_snake(s):
    new_string = re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()
    return new_string
