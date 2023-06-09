# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from abc import ABC, abstractmethod
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
        self.valid_types = ['string', 'iso-datetime', 'iso-duration', 'string-drop-list',
                            'string-check-list', 'file-drop-list', 'file-check-list', 'boolean']

        # Disallowed element types
        self.dis_elem_types = [datetime.datetime, datetime.date]

        # Track the suite and platform that the user may input through the prepare_config path
        self.suite_to_run = suite
        self.platform = platform
        #user_inputs_dict = {}
        #user_inputs_dict['suite_to_run'] = suite
        #user_inputs_dict['platform'] = platform

        # Open the platform specific defaults
        platform_dict_file = os.path.join(swell_path, 'deployment', 'platforms', platform,
                                          'suite_questions.yaml')
        with open(platform_dict_file, 'r') as platform_dict_file_open:
            platform_dict_str = platform_dict_file_open.read()

        # Dictionary of templates to use whenever opening a file
        self.platform_dictionary = yaml.safe_load(platform_dict_str) # Use for 'defer_to_platform' default

        # Open Master task questions yaml
        with open(os.path.join(swell_path, 'tasks', 'task_questions.yaml'), 'r') as ymlfile:
            self.all_task_questions = yaml.safe_load(ymlfile)

    # ----------------------------------------------------------------------------------------------

    def key_passer(self, key, el_dict):

        if key != 'fixed_options':

            # Validate the element dictionary
            self.validate_dictionary(el_dict)

            # Extract type
            type = el_dict['type']

            # Check that the key does not have a dependency
            depends_flag = True
            if 'depends' in el_dict.keys():
                dep_key = el_dict['depends']['key']
                dep_val = el_dict['depends']['value']
                if self.experiment_dict[dep_key] != dep_val:
                    depends_flag = False
                    #if key == self.end_key:
                    #    change_check = self.before_next()

            # In this case the key is not expected to refer to a sub dictionary but have
            # everything needed in the elements dictionary
            if depends_flag:
                el_dict['default_value'] = self.show_deference(key, el_dict['default_value'])
                el_dict['default_value'] = self.get_answer(key, el_dict)
                #if key == self.end_key:
                #    change_check = self.before_next()
                #    if isinstance(change_check, dict):
                #        el_dict = change_check
                self.add_to_experiment_dictionary(key, el_dict)

        return

    # ----------------------------------------------------------------------------------------------

    def set_model_template(self, model):
        swell_path = self.install_path
        task_file = camel_to_snake('GetBackground')

        # Open model specific defaults
        model_inputs_dict_file = os.path.join(swell_path, 'configuration',
                                              'jedi/interfaces/' + model,
                                              'tasks', task_file + '.yaml')

        with open(model_inputs_dict_file, 'r') as model_inputs_open:
            model_template_dictionary = yaml.safe_load(model_inputs_open.read())

        return model_template_dictionary

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

    def update_experiment_dictionary(self, key, new_value):
        if self.model is not None:
            self.experiment_dict['models'][self.model][key] = new_value
        else:
            self.experiment_dict[key] = new_value

    # ----------------------------------------------------------------------------------------------

    def get_tasks(self, task_list, task_type):
        tasks_path = os.path.join(self.install_path, 'tasks/')
        task_collector = {}
        if task_type == 'base':
            self.model_task = False
        elif task_type == 'model':
            self.model_task = True
        for t in task_list:
            name = t
            name = camel_to_snake(name)
            t = name
            task_file = t + '.yaml'
            task_dict = self.read_dictionary_file(os.path.join(tasks_path, task_file))
            if 'task_prerequisites' in task_dict.keys():
                for pr in task_dict['task_prerequisites']:
                    pr = camel_to_snake(pr)
                    if pr in task_collector.keys():
                        task_dict.pop('task_prerequisites')
                    else:
                        print('ABORT')
            if task_dict:
                task_collector[t] = task_dict
        return task_collector

    # ----------------------------------------------------------------------------------------------

    def build_question_dictionary(self, match, get_dependents):
        question_dictionary = {}
        for k, v in self.all_task_questions.items():
            if match in v['tasks']:
                if get_dependents:
                    if 'depends' in v.keys():
                        question_dictionary[k] = v
                else:
                    if 'depends' not in v.keys():
                        question_dictionary[k] = v
        return question_dictionary    

    # ----------------------------------------------------------------------------------------------

    def dictionary_comber(self, matches):

        for m in matches:
            self.current_dictionary = {}
            question_dict = self.build_question_dictionary(m, get_dependents=False)
            dependent_dict = self.build_question_dictionary(m, get_dependents=True)
            question_dict.update(dependent_dict)
            for k, v in question_dict.items():
                if k in self.experiment_dict.keys():
                    pass
                else:
                    self.key_passer(k, v)
            self.before_next()
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

        val['default_value'] = self.show_deference(key, val['default_value'])

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

        val['default_value'] = self.show_deference(key, val['default_value'])

        val['default_value'] = self.get_answer(key, val)

        self.add_to_experiment_dictionary(key, val)

        # Look in suite_to_run dir and check for suite yaml file, if not, grep the flow.cylc file

        # Check which suite to run, check for suite_questions yaml, and grep flow file
        self.directory = os.path.join(self.directory, self.suite_to_run)
        suite_questions_path = os.path.join(self.directory, 'suite_questions.yaml')

        if os.path.exists(suite_questions_path):
            print('SUITE QUESTIONS FILE FOUND. NEED TO CREATE FUNCTION FOR THIS')
        else:
            pass

        matches = self.open_flow()

        return matches

    # ----------------------------------------------------------------------------------------------

    def show_deference(self, key, default):

        if 'defer' in default:
            pass
        else:
            return default

        if 'platform' in default:
            default = self.platform_dictionary[key]['default_value']
        elif 'model' in default:
            # Will need something like the following
            print('No code for model deference')
            #default = self.model_dictionary[key]['default_value']

        return default

    # ----------------------------------------------------------------------------------------------

    def open_flow(self):
        #open text file in read mode
        cylc_file = open(os.path.join(self.directory, 'flow.cylc'), "r")
 
        #read whole file to a string
        data = cylc_file.read()
 
        #close file
        cylc_file.close()

        # Find the double bracket items in the Tasks section of the flow file to ID required tasks 
        task_s = data[(data.find('Tasks')):]
        pattern = r"\[\[(.*?)\]\]"  # Regex pattern to match characters inside double brackets
        matches = re.findall(pattern, task_s)  # Find all matches in the text
        matches = [x for x in matches if not '[' in x]

        print('\n Following tasks selected for configuration: \n',
              '\n ************ \n',
              matches,
              '\n ************ \n')

        ## CHECK FOR -M FOR MODELS WHEN WE WORK ON MODEL PART

        return matches

    # ----------------------------------------------------------------------------------------------

    def execute(self):
        # then open the suite_to_run selected
        # check_widgets goes in cli
        # defaults gets nothing

        print(f"Now editing the {os.path.basename(self.directory)} YAML file.")

        # Set current dictionary variable which is needed for answer changes
        self.current_dictionary = {}

        # Get answers for the suite YAML file

        matches = self.suite_setup()

        self.before_next()

        # Open the platform specific task template and reassign platform dictionary
        platform_dict_file = os.path.join(self.install_path, 'deployment', 'platforms', self.platform,
                                          'task_questions.yaml')

        with open(platform_dict_file, 'r') as platform_dict_file_open:
            platform_dict_str = platform_dict_file_open.read()

        # Dictionary of templates to use whenever opening a file
        self.platform_dictionary = yaml.safe_load(platform_dict_str) # Use for 'defer_to_platform' default

        # Iterate over main task dictionary and get answers
        
        self.dictionary_comber(matches)

        return

        # The subclass has to implement an execute method since this is how it is called into
        # action.
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
