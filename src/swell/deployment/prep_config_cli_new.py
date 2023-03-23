# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import glob
import os
import re
import sys

import questionary

from swell.deployment.prep_config_base_new import PrepConfigBase
from swell.swell_path import get_swell_path

# --------------------------------------------------------------------------------------------------


class PrepConfigCli(PrepConfigBase):

    def execute(self, dictionary=None):

        # Set dictionary to use in this scope
        if dictionary is None:
            dictionary = self.dictionary

        print(f"Now editing the {self.directory.split('/')[-1]} YAML file.")

        # Get final key in yaml before fixed options
        self.dictionary = self.open_dictionary()

        key_list = list(self.dictionary.keys())

        new_dictionary = {}
        for i, key in enumerate(key_list):
            if 'tasks' in key:
                if 'model' not in key:
                    task_collector = self.get_tasks(self.dictionary['tasks'], 'base')
                    for task in task_collector:
                        for element in task_collector[task]:
                            new_dictionary[element] = task_collector[task][element]
                elif 'model' in key:
                    if 'models' not in new_dictionary.keys():
                        new_dictionary['models'] = {}
                    model_list = self.model_check()
                    for model in model_list:
                        self.model_name = model
                        new_dictionary['models'][model] = {}
                        task_collector = self.get_tasks(self.dictionary['model_tasks'], 'model')
                        for task in task_collector:
                            for element in task_collector[task]:
                                new_dictionary['models'][model][element] = task_collector[task][element]
                key_list = list(new_dictionary.keys())
                self.dictionary = new_dictionary
            else:
                new_dictionary[key] = self.dictionary[key]
        dictionary = new_dictionary

        del(new_dictionary)

        end_key = None

        if 'fixed_options' in key_list:
            fixed_idx = key_list.index('fixed_options')
            key_list.pop(fixed_idx)
        end_key = key_list[-1]
 
        # Reset key list so fixed options is removed
        self.exec_keys = []

        def key_passer(key, el_dict):

            if key != 'fixed_options':

                # Validate the element dictionary
                if key != 'tasks':
                    self.validate_dictionary(el_dict)

                # Extract type
                type = el_dict['type']

                # If the type is not another file add to dictionary
                if 'file' not in type:

                    # Check that the key does not have a dependency
                    depends_flag = True
                    if 'depends' in el_dict.keys():
                        dep_key = el_dict['depends']['key']
                        dep_val = el_dict['depends']['value']
                        if self.experiment_dict[dep_key] != dep_val:
                            depends_flag = False
                            if key == end_key:
                                change_check = self.before_next()

                    # In this case the key is not expected to refer to a sub dictionary but have
                    # everything needed in the elements dictionary
                    if depends_flag:
                        el_dict['default_value'] = self.check_widgets(key, el_dict)
                        # Register the added experiment element key
                        self.exec_keys.append(key)
                        if key == end_key:
                            change_check = self.before_next()
                            if isinstance(change_check, dict):
                                el_dict = change_check
                        self.add_to_experiment_dictionary(key, el_dict)

                elif 'file-drop-list' in type:

                    # Add the choice to the dictionary
                    # If you wanted more suite options, you'd need to add directories for them at
                    # the suites/ level
                    el_dict['default_value'] = self.check_widgets(key, el_dict)

                    # Register the added experiment element key
                    self.exec_keys.append(key)

                    # Check if the user wants to change any answers
                    change_check = self.before_next()
                    if isinstance(change_check, dict):
                        el_dict = change_check
                    self.add_to_experiment_dictionary(key, el_dict)

                    # Go into directory based on drop_list method
                    if 'suite' in key:
                        self.directory = os.path.join(self.directory, key)
                        self.filename = el_dict['default_value']

                    # Open next level down dictionary and recursively add
                    self.execute(self.open_dictionary())

            elif key == 'fixed_options':

                for fixed_key in el_dict:

                    self.add_to_experiment_dictionary(fixed_key, el_dict[fixed_key])

            return

        for key in dictionary:
            # Element dictionary
            if key == 'models':
                for m in dictionary[key]:
                    self.model = m
                    for k in dictionary[key][m]:
                        el_dict = dictionary[key][m][k]
                        key_passer(k, el_dict)
            else:
                self.model = None
                el_dict = dictionary[key]
                key_passer(key, el_dict)

        return

    def check_widgets(self, key, val):
        print('\n')
        widget_type = val['type']
        quest = val['prompt']
        default = val['default_value']
        if widget_type == 'string':
            answer = self.make_string_widget(quest, default, questionary.text)
        elif 'drop-list' in widget_type:
            if 'file' in widget_type:
                options = 'file'
            elif 'string' in widget_type:
                options = val['options']
            answer = self.make_drop_widget(key, quest, options, default, questionary.select)
        elif widget_type == 'boolean':
            answer = self.make_boolean(quest, default, questionary.confirm)
        elif widget_type == 'iso-datetime':
            answer = self.make_datetime(quest, default, questionary.text)
        elif widget_type == 'iso-duration':
            answer = self.make_duration(quest, default, questionary.text)
        elif 'check-list' in widget_type:
            if 'file' in widget_type:
                options = 'file'
            elif 'string' in widget_type:
                options = val['options']
            answer = self.make_check_widget(quest, options, default, questionary.checkbox)
        else:
            answer = default

        if answer in ['', []] and widget_type != 'file-check-list':
            answer = default

        if answer == 'EXIT':
            print('Exiting swell prepper...')
            sys.exit()

        return answer

    def make_string_widget(self, quest, default, prompt):
        answer = prompt(f"{quest} [{default}]", default=default).ask()

        return answer

    def make_drop_widget(self, method, quest, options, default, prompt):
        if options == 'file':
            new_path = os.path.join(self.directory, method, '*.yaml')
            suite_list = [x.split('/')[-1].split('.')[0] for x in glob.glob(new_path)]
            # Make sure no python directories are included
            suite_list = list(filter(lambda a: a != '__pycache__', suite_list))
            choices = suite_list
        else:
            if options == 'use_method':
                if 'platform' in method:
                    method_dir = 'deployment/platforms/'
                new_path = os.path.join(os.path.dirname(self.directory), method_dir, '*/')
                suite_list = [x.split('/')[-2] for x in glob.glob(new_path)]
                # Make sure no python directories are included
                suite_list = list(filter(lambda a: a != '__pycache__', suite_list))
                options = suite_list
            choices = options
        answer = prompt(quest, choices=choices, default=default).ask()

        return answer

    def make_boolean(self, quest, default, prompt):
        answer = prompt(quest, default=default, auto_enter=False).ask()

        return answer

    def make_datetime(self, quest, default, prompt):

        class dtValidator(questionary.Validator):
            def validate(self, document):
                r = re.compile('\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ')  # noqa
                if r.match(document.text) is None and document.text != 'EXIT':
                    raise questionary.ValidationError(
                        message="Please enter a datetime with the following format: " +
                                "YYYY-MM-DDThh:mm:ssZ",
                        cursor_position=len(document.text),
                    )

        answer = prompt(f"{quest}\n[format YYYY-MM-DDThh:mm:ssZ e.g. {default}]", default=default,
                        validate=dtValidator).ask()

        return answer

    def make_duration(self, quest, default, prompt):

        class durValidator(questionary.Validator):
            def validate(self, document):
                r = re.compile('PT\d{1,2}H')  # noqa
                if r.match(document.text) is None and document.text != 'EXIT':
                    raise questionary.ValidationError(
                        message="Please enter a duration with the following format: PThhH",
                        cursor_position=len(document.text),
                    )

        if isinstance(default, list):
            answer_list = []
            answer = ''
            r = re.compile('T\d\d')  # noqa
            while answer != 'q':
                answer = prompt(f"{quest}\n[format Thh e.g. {default}]",
                                validate=lambda text: True if r.match(text) is not None or
                                text == 'q'
                                else "Please enter a duration with the following format: Thh",
                                default=default).ask()
                if answer == 'q':
                    pass
                else:
                    answer_list.append(answer)
        elif isinstance(default, str):
            answer = prompt(f"{quest}\n[format PThhH e.g. {default}]",
                            validate=durValidator, default=default).ask()

        return answer

    def make_check_widget(self, quest, options, default, prompt):
        if options == 'file':
            dir_list = os.listdir(self.directory)
            new_path = os.path.join(self.directory, '*/')
            suite_list = [x.split('/')[-2] for x in glob.glob(new_path)]
            choices = suite_list
            default = None
        else:
            if options == 'use_method':
                choices = default
                default = default[0]
                if self.model is not None:
                    files = glob.glob(os.path.join(self.install_path,
                                                   'configuration/jedi/interfaces',
                                                   self.model,
                                                   'observations/*.yaml'))
                    # Do not include obsop_name_map.yaml in the list of observations
                    files = list(filter(lambda a: 'obsop_name_map' not in a, files))
                    choices = [x.split('/')[-1].split('.')[0] for x in files]
            else:
                choices = options
                if default is None:
                    pass
                else:
                    default = default[0]
        answer = prompt(quest, choices=choices,
                        default=default,
                        validate=lambda text: True if text != []
                        else 'Please select one option').ask()
        return answer

    def before_next(self):
        changer = self.make_boolean('Do you wish to change any of your entries?',
                                    False,
                                    questionary.confirm)
        if changer:
            keys = self.exec_keys
            #print(keys, '\n', self.dictionary.keys(), '\n')
            for k in keys:
                if k not in list(self.dictionary.keys()):
                    non_exec_idx = keys.index(k)
                    keys.pop(non_exec_idx)
            #print(keys)
            # Show user key change options and retrieve new values
            change_keys = self.make_check_widget('Which elements would you like to change?',
                                                 keys,
                                                 None,
                                                 questionary.checkbox)
            for k in change_keys:
                changed_dict = self.dictionary[k]
                new_default_value = self.check_widgets(k, changed_dict)
                if 'file' in changed_dict['type']:
                    changed_dict['default_value'] = new_default_value
                    return changed_dict
                elif k == self.exec_keys[-1]:
                    changed_dict['default_value'] = new_default_value
                    return changed_dict
                else:
                    self.update_experiment_dictionary(k, new_default_value)
            return None

    def model_check(self):
        model_options = glob.glob(os.path.join(self.install_path, 'configuration',
                                       'jedi/interfaces/', '*/'))

        model_options = [x.split('/')[-2] for x in model_options]

        selected_models = self.make_check_widget('Which models?', model_options, default=['geos_ocean'], prompt=questionary.checkbox)

        if 'None' in selected_models:
            selected_models = []

        return selected_models

# --------------------------------------------------------------------------------------------------

