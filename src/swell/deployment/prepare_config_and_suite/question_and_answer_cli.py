# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import re
import sys
from typing import Union

import questionary
from questionary import Choice

from swell.utilities.logger import Logger
from swell.utilities.swell_questions import WidgetType


# --------------------------------------------------------------------------------------------------


class GetAnswerCli:

    def get_answer(self, logger: Logger, key: str, val: dict):
        prompt = val['prompt']
        default = val['default_value']
        widget_type = val['widget_type']
        options = val['options']
        
        if widget_type.is_drop_list:
            answer = self.make_drop_widget(prompt, default, options, widget_type)
        elif widget_type.is_check_list:
            answer = self.make_check_widget(prompt, default, options, widget_type)
        elif widget_type == WidgetType.BOOLEAN:
            answer = self.make_boolean_widget(prompt, default)

        else:
            answer = self.make_generic_widget(prompt, default, options, widget_type)
            
        if answer in ['', []] and widget_type != WidgetType.FILE_CHECK_LIST:
            answer = default
        
        if answer == 'EXIT' or answer is None:
            logger.abort('Exiting Swell prepper...')

        return answer
        
    # --------------------------------------------------------------------------------------------------
            
    def make_generic_widget(self, prompt: str, default, options: list, widget_type: WidgetType):
        default = str(default)

        answer = questionary.text(f"{prompt} [{default}]", validate=lambda text: True if widget_type.validate_value(text) else f'Please enter a value of type: {widget_type.value}', default=default).ask()
        
        return answer

    # --------------------------------------------------------------------------------------------------
        
    def make_drop_widget(self, prompt: str, default, options: list, widget_type: WidgetType):
        default = str(default)
        choices = [str(x) for x in options]

        answer = questionary.select(prompt, choices=choices, default=default).ask()
        
        return answer
    
    # --------------------------------------------------------------------------------------------------
        
    def make_check_widget(self, prompt: str, default, options: list, widget_type: WidgetType):
        choices = options.copy()

        if isinstance(default, list):
            for i, c in enumerate(choices):
                if c in default:
                    choices[i] = Choice(c, checked=True)
                else:
                    choices[i] = Choice(c, checked=False)
            default = None

        answer = questionary.checkbox(prompt, choices=choices, default=default, validate=lambda text: True if (widget_type.validate_value(text) and text != []) else 'Select at least one option, or selected option may be of invalid type').ask()
        
        return answer
    
    # --------------------------------------------------------------------------------------------------
    
    def make_boolean_widget(self, prompt: str, default: bool):
        
        answer = questionary.confirm(prompt, default=default, auto_enter=False).ask()
        
        return answer
    
    # --------------------------------------------------------------------------------------------------
