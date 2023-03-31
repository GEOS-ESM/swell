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
from questionary import Choice

from swell.deployment.prep_config_base import PrepConfigBase
from swell.swell_path import get_swell_path

# --------------------------------------------------------------------------------------------------


class PrepConfigCli(PrepConfigBase):

    def get_answer(self, key, val):
        # Set questionary variable
        widget_type = val['type']
        quest = val['prompt']
        default = val['default_value']

        # Check questionary input type and ask user
        print('\n')
        if widget_type == 'string':
            answer = self.make_string_widget(quest, default, questionary.text)
        elif 'drop-list' in widget_type:
            options = val['options']
            answer = self.make_drop_widget(key, quest, options, default, questionary.select)
        elif widget_type == 'boolean':
            answer = self.make_boolean(quest, default, questionary.confirm)
        elif widget_type == 'iso-datetime':
            answer = self.make_datetime(quest, default, questionary.text)
        elif widget_type == 'iso-duration':
            answer = self.make_duration(quest, default, questionary.text)
        elif 'check-list' in widget_type:
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

    # ----------------------------------------------------------------------------------------------

    def get_models(self):

        model_options = glob.glob(os.path.join(self.model_path, '*'))
        model_options.sort()

        print('TEST', model_options)

        model_options = [os.path.basename(x) for x in model_options]

        choices = []

        for mod in model_options:
            if mod in self.model_choices:
                choices.append(Choice(mod, checked=True))
            else:
                choices.append(Choice(mod, checked=False))

        selected_models = self.make_check_widget('Which models?', choices, default = None, prompt=questionary.checkbox)

        if 'None' in selected_models:
            selected_models = []

        return selected_models

    # ----------------------------------------------------------------------------------------------

    def make_string_widget(self, quest, default, prompt):
        answer = prompt(f"{quest} [{default}]", default=default).ask()

        return answer

    # ----------------------------------------------------------------------------------------------

    def make_drop_widget(self, method, quest, options, default, prompt):
        if options == 'use_method':
            if method == 'platform':
                method_dir = 'deployment/platforms/'
            elif method == 'suite_to_run':
                method_dir = 'suites_new/suite_to_run'
            new_path = os.path.join(os.path.dirname(self.directory), method_dir, '*')
            suite_list = [os.path.splitext(os.path.basename(x))[0] for x in glob.glob(new_path)]
            # Make sure no python directories are included
            suite_list = list(filter(lambda a: a != '__pycache__' and a != '__init__', suite_list))
            choices = suite_list
        else:
            choices = options
        answer = prompt(quest, choices=choices, default=default).ask()

        return answer

    # ----------------------------------------------------------------------------------------------

    def make_boolean(self, quest, default, prompt):
        answer = prompt(quest, default=default, auto_enter=False).ask()

        return answer

    # ----------------------------------------------------------------------------------------------

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

    # ----------------------------------------------------------------------------------------------

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

    # ----------------------------------------------------------------------------------------------

    def make_check_widget(self, quest, options, default, prompt):
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
                choices = [os.path.splitext(os.path.basename(x))[0] for x in files]
        else:
            choices = options

        answer = prompt(quest, choices=choices, default=default,
                        validate=lambda text: True if text != []
                        else 'Please select one option').ask()
        return answer

    # ----------------------------------------------------------------------------------------------

    def before_next(self):
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
                    changed_dict['default_value'] = new_default_value
                    return changed_dict
                elif k == self.exec_keys[-1]:
                    changed_dict['default_value'] = new_default_value
                    return changed_dict
                else:
                    self.update_experiment_dictionary(k, new_default_value)
            return None

# --------------------------------------------------------------------------------------------------

