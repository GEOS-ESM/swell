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

from swell.deployment.prep_config_base import PrepConfigBase


# --------------------------------------------------------------------------------------------------


class PrepConfigCli(PrepConfigBase):

    def execute(self, dictionary=None):

        # Set dictionary to use in this scope
        if dictionary is None:
            dictionary = self.dictionary

        print(f"Now editing the {self.directory.split('/')[-1]} YAML file.")

        for key in dictionary:
            # Element dictionary
            el_dict = dictionary[key]

            if key != 'fixed_options':

                # Validate the element dictionary
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

                    # In this case the key is not expected to refer to a sub dictionary but have
                    # everything needed in the elements dictionary
                    if depends_flag:
                        el_dict['default_value'] = self.check_widgets(key, el_dict)
                        self.add_to_experiment_dictionary(key, el_dict)

                elif 'file-drop-list' in type:

                    # Add the choice to the dictionary
                    # If you wanted more suite options, you'd need to add directories for them at
                    # the suites/ level
                    el_dict['default_value'] = self.check_widgets(key, el_dict)
                    self.add_to_experiment_dictionary(key, el_dict)
                    self.before_next()

                    # In this case the key refers to a single sub dictionary that involves opening
                    # that dictionary and recursively calling this routine.

                    # First append the directory and filename to denote moving to the sub dictionary
                    self.append_directory_and_filename(el_dict['default_value'])

                    # Open next level down dictionary and recursively add
                    self.execute(self.open_dictionary())

                    # As we come back from the sub dictionary subtract the directory and filename
                    self.subtract_directory_and_filename()

                elif 'file-check-list' in type:

                    # Add the choice to the dictionary
                    el_dict['default_value'] = self.check_widgets(key, el_dict)
                    self.add_to_experiment_dictionary(key, el_dict)

                    # In this case the key asks the user to provide a list of items that correspond
                    # to sub dictionaries. Inside a loop this method is called recursively.
                    options = el_dict['default_value']
                    for option in options:

                        # If the key is models change the internal model to match this model
                        if key == 'model_components':
                            self.update_model(option)

                        self.append_directory_and_filename(option)
                        self.execute(self.open_dictionary())
                        self.subtract_directory_and_filename()

                        if key == 'model_components':
                            self.update_model(None)

            else:

                for fixed_key in el_dict:

                    self.add_to_experiment_dictionary(fixed_key, el_dict[fixed_key])

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

        return answer

    def make_string_widget(self, quest, default, prompt):
        answer = prompt(f"{quest} [{default}]", default=default).ask()

        return answer

    def make_drop_widget(self, method, quest, options, default, prompt):
        if options == 'file':
            new_path = os.path.join(self.directory, '*/')
            suite_list = [x.split('/')[-2] for x in glob.glob(new_path)]
            choices = suite_list
        else:
            if options == 'use_method':
                if 'platform' in method:
                    method_dir = 'deployment/platforms/'
                new_path = os.path.join(os.path.dirname(self.directory), method_dir, '*/')
                suite_list = [x.split('/')[-2] for x in glob.glob(new_path)]
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
                if r.match(document.text) is None:
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
                if r.match(document.text) is None:
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
                                else "Please enter a duration with the following format: Thh").ask()
                if answer == 'q':
                    pass
                else:
                    answer_list.append(answer)
        elif isinstance(default, str):
            answer = prompt(f"{quest}\n[format PThhH e.g. {default}]",
                            validate=durValidator).ask()

        return answer

    def make_check_widget(self, quest, options, default, prompt):
        # Can use questionary Choice() operator instead of list of strings
        # Check for defaults and use checked=True for each
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
        changer = self.make_boolean('Do you wish to change any of your entries?', False, questionary.confirm) 
        if changer:
            print('changing')
            change_keys = self.make_check_widget('Which elements would you like to change?', keys, None, questionary.checkbox)
            #changed_dict = {}
            for k in change_keys:
                changed_dict = self.dictionary[k]
                changed_dict['default_value'] = self.check_widgets(k, changed_dict)
                self.update_experiment_dictionary(k, changed_dict)
        return None

# --------------------------------------------------------------------------------------------------
