# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
from typing import Literal

from swell.swell_path import get_swell_path

# --------------------------------------------------------------------------------------------------


def check_question_order():
    question_file = os.path.join(get_swell_path(), 'configuration', 'question_defaults.py')

    with open(question_file, 'r') as f:
        lines = f.readlines()

    in_task_section = False

    task_questions = []
    suite_questions = []

    for line in lines:
        if 'class ' in line:
            if '(SuiteQuestion)' in line:
                if in_task_section:
                    raise Exception('Suite and Task questions are mixed up, please ensure '
                                    'that suite questions come first, then task questions.')

                question = line.split('class ')[1].split('(SuiteQuestion)')[0].strip()
                suite_questions.append(question)
            elif '(TaskQuestion)' in line:
                in_task_section = True
                question = line.split('class ')[1].split('(TaskQuestion)')[0].strip()

                task_questions.append(question)

    check_order('task', task_questions)
    check_order('suite', suite_questions)

# --------------------------------------------------------------------------------------------------


def check_order(qtype: Literal['task', 'suite'], check_list: list):
    in_order = True

    sorted_list = sorted(check_list)

    max_chars = max([len(item) for item in sorted_list]) + 4

    order_str = 'Order in file: '
    order_str += '{tabs}> Should be:\n'.format(tabs='-'*(max_chars-len(order_str)))

    for i, sorted_item in enumerate(sorted_list):
        check_item = check_list[i]

        tab_char = ' '
        if check_item != sorted_item:
            in_order = False
            tab_char = '-'

        tabs = tab_char*((max_chars-len(check_item)))

        order_str += f'{check_item} {tabs}> {sorted_item}\n'

    if not in_order:
        raise Exception(f'\nQuestions in the {qtype} section are not in order, '
                        f'please rearrange according to the following:\n\n{order_str}')


# --------------------------------------------------------------------------------------------------
