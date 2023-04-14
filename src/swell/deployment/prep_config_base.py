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

    def __init__(self, logger, dictionary_file, suite, platform, models):

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
        self.model_choices = models

        # Experiment dictionary to be created and used in swell
        self.experiment_dict = {}

        # Comment dictionary to be created and used to add comments to config file
        self.comment_dict = {}

        # Dictionary validation things
        self.valid_types = ['string', 'iso-datetime', 'iso-duration', 'string-drop-list',
                            'string-check-list', 'file-drop-list', 'file-check-list', 'boolean']

        # Disallowed element types
        self.dis_elem_types = [datetime.datetime, datetime.date]

        # Track the suite and platform that the user may input through the prepare_config path
        user_inputs_dict = {}
        user_inputs_dict['suite_to_run'] = suite
        user_inputs_dict['platform'] = platform

        # Open the platform specific defaults
        platform_dict_file = os.path.join(swell_path, 'deployment', 'platforms', platform,
                                          'experiment.yaml')
        with open(platform_dict_file, 'r') as platform_dict_file_open:
            platform_dict_str = platform_dict_file_open.read()

        # Render the templates in the platform dictionary using user inputs
        platform_dict_str = template_string_jinja2(self.logger, platform_dict_str, user_inputs_dict)

        # Dictionary of templates to use whenever opening a file
        self.platform_template_dictionary = yaml.safe_load(platform_dict_str)
        self.platform_template_dictionary.update(user_inputs_dict)

    # ----------------------------------------------------------------------------------------------

    def set_end_key(self, key_list):
        if 'fixed_options' in key_list:
            fixed_idx = key_list.index('fixed_options')
            key_list.pop(fixed_idx)
        self.end_key = key_list[-1]
        return key_list

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
                    if key == self.end_key:
                        change_check = self.before_next()

            # In this case the key is not expected to refer to a sub dictionary but have
            # everything needed in the elements dictionary
            if depends_flag:
                el_dict['default_value'] = self.get_answer(key, el_dict)
                # Register the added experiment element key
                self.exec_keys.append(key)
                if key == self.end_key:
                    change_check = self.before_next()
                    if isinstance(change_check, dict):
                        el_dict = change_check
                self.add_to_experiment_dictionary(key, el_dict)

        elif key == 'fixed_options':

            for fixed_key in el_dict:

                self.add_to_experiment_dictionary(fixed_key, el_dict[fixed_key])

        return

    # ----------------------------------------------------------------------------------------------

    def before_next(self, method):
        if method == 'defaults':
            return None

        changer = self.make_boolean('Do you wish to change any of your entries?',
                                    False,
                                    questionary.confirm)
        if changer:
            keys = self.exec_keys
            for k in keys:
                if k not in list(self.dictionary.keys()):
                    non_exec_idx = keys.index(k)
                    keys.pop(non_exec_idx)
            # Show user key change options and retrieve new values
            change_keys = self.make_check_widget('Which elements would you like to change?',
                                                 keys,
                                                 None,
                                                 questionary.checkbox)

            for k in change_keys:
                changed_dict = self.dictionary[k]
                new_default_value = self.check_widgets(k, changed_dict)
                if 'file' in changed_dict['type']:
                    # going to need to change this now because file in type is no longer there
                    changed_dict['default_value'] = new_default_value
                    return changed_dict
                elif k == self.exec_keys[-1]:
                    changed_dict['default_value'] = new_default_value
                    return changed_dict
                else:
                    self.update_experiment_dictionary(k, new_default_value)
            return None

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

    def open_dictionary(self):

        # Append the filename according the type of files
        filename_ext = os.path.join(self.directory, self.filename + '.yaml')

        # Open file into dictionary
        dictionary = self.read_dictionary_file(filename_ext)

        # Check that dictionary contained something
        if dictionary is None:
            self.logger.abort(f'Dictionary at {filename_ext} returned {None} when opened')

        return dictionary

    # ----------------------------------------------------------------------------------------------

    def read_dictionary_file(self, dictionary_file):

        # Open file as a string
        with open(dictionary_file, 'r') as dictionary_file_open:
            dictionary_str = dictionary_file_open.read()

        if self.model_task:
            template_dictionary = self.set_model_template(self.model_name)
        else:
            template_dictionary = self.platform_template_dictionary

        # Render the templates using the template dictionary
        dictionary_str = template_string_jinja2(self.logger, dictionary_str,
                                                template_dictionary)

        # Convert string to dictionary
        return yaml.safe_load(dictionary_str)

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

    def update_model(self, model):

        if model is None:
            self.model = None
        else:
            self.model = model

            # If models list not already in the dictionary added
            if 'models' not in self.experiment_dict.keys():
                self.experiment_dict['models'] = {}

            # If specific model dictionary not added to the list of model then add it
            if self.model not in self.experiment_dict['models'].keys():
                self.experiment_dict['models'][self.model] = {}

    # ----------------------------------------------------------------------------------------------

    def add_to_experiment_dictionary(self, key, element_dict):

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

    def expand_tasks(self, key_list, dictionary):
        new_dictionary = {}
        for i, key in enumerate(key_list):
            if 'tasks' in key:
                if 'model' not in key:
                    task_collector = self.get_tasks(dictionary['tasks'], 'base')
                    for task in task_collector:
                        for element in task_collector[task]:
                            new_dictionary[element] = task_collector[task][element]
                elif 'model' in key:
                    if 'models' not in new_dictionary.keys():
                        new_dictionary['models'] = {}

                    # Setting model options from available models in interfaces
                    self.model_options = glob.glob(os.path.join(self.install_path,
                                                                'configuration',
                                                                'jedi/interfaces/',
                                                                '*/'))

                    model_list = self.get_models()
                    for model in model_list:
                        self.model_name = model
                        new_dictionary['models'][model] = {}
                        task_collector = self.get_tasks(dictionary['model_tasks'], 'model')
                        for task in task_collector:
                            for element in task_collector[task]:
                                new_dictionary['models'][model][element] = \
                                    task_collector[task][element]
                key_list = list(new_dictionary.keys())
            else:
                new_dictionary[key] = dictionary[key]
        dictionary = new_dictionary

        del new_dictionary

        return dictionary

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

    def dictionary_comber(self, dictionary):
        # Set key list and expand task lists
        key_list = list(dictionary.keys())
        dictionary = self.expand_tasks(key_list, dictionary)

        # Save dictionary as self.dictionary for use in prep_config_cli.before_next()
        self.dictionary = dictionary

        # Check for fixed options in key list and set end key
        key_list = self.set_end_key(key_list)

        # Create empty executable key list which will track which keys are executed
        self.exec_keys = []

        # Iterate over dictionary
        for key in dictionary:
            # Element dictionary
            if key == 'models':
                for m in dictionary[key]:
                    self.model = m
                    for k in dictionary[key][m]:
                        el_dict = dictionary[key][m][k]
                        self.key_passer(k, el_dict)
            else:
                self.model = None
                el_dict = dictionary[key]
                self.key_passer(key, el_dict)

        return

    # ----------------------------------------------------------------------------------------------

    def execute(self):
        # then open the suite_to_run selected
        # check_wdigets goes in cli
        # defaults gets nothing

        print(self.directory, self.filename)

        print(f"Now editing the {os.path.basename(self.directory)} YAML file.")

        # Get answers for the suite YAML file
        suite_dictionary = self.open_dictionary()

        self.dictionary_comber(suite_dictionary)

        # Check which suite to run
        self.directory = os.path.join(self.directory, 'suite_to_run')
        self.filename = self.experiment_dict['suite_to_run']

        suite_to_run_dictionary = self.open_dictionary()

        self.dictionary_comber(suite_to_run_dictionary)

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
