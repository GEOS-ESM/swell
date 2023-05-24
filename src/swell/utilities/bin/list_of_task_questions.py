#!/usr/bin/env python

# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


# standard imports
from collections import OrderedDict
import os
import pathlib
import yaml

# swell imports
from swell.swell_path import get_swell_path
from swell.utilities.logger import Logger


# --------------------------------------------------------------------------------------------------


def main():

    # Create a logger
    logger = Logger('ListOfTaskQuestions')

    # Path to JEDI interface code
    swell_path = get_swell_path()
    jedi_tasks_path = pathlib.Path(os.path.join(swell_path, 'tasks'))

    # All python files
    task_codes = jedi_tasks_path.rglob("*py")

    # All lines of all task files
    raw_task_code_lines = []
    task_names = []

    # Output file
    outfile_yaml = os.path.join(swell_path, 'tasks', 'questions.yaml')

    # Read input file into dictionary
    if os.path.exists(outfile_yaml):
        with open(outfile_yaml, 'r') as ymlfile:
            question_dict = yaml.safe_load(ymlfile)
    else:
        question_dict = {}

    for task_code in task_codes:

        if '__init__.py' not in str(task_code) and 'task_base.py' not in str(task_code):

            with open(task_code, 'r') as file:
                file_lines = file.read().split('\n')

                for file_line in file_lines:
                    if 'self.config_get' in file_line:
                        raw_task_code_lines.append(file_line.split('=')[1].strip())
                        task_names.append(os.path.basename(str(task_code)).split('.')[0])

    # Extract just the config key from the string
    config_keys = []
    for raw_task_code_line in raw_task_code_lines:

        config_key = raw_task_code_line.replace('self.config_get(', '')
        config_key = config_key.replace(')', '')
        config_key = config_key.split(',')[0].strip()
        config_key = config_key.split('#')[0].strip()
        config_key = config_key.replace('\'', '')

        config_keys.append(config_key)

    # For each key create lists of tasks
    unique_keys = sorted(list(set(config_keys)))

    # question to task dictionary
    question_to_tasks = {}

    # Output file
    outfile_yaml = os.path.join(swell_path, 'tasks', 'questions.yaml')
    outfile = open(outfile_yaml, 'w')

    # Task for each key
    for unique_key in unique_keys:

        tasks = []

        for task_name, config_key in zip(task_names, config_keys):

            if unique_key == config_key:

                tasks.append(task_name)

        question_to_tasks = {}

        if unique_key in question_dict:
            question_to_tasks[unique_key] = question_dict[unique_key]

            question_dict_key = question_dict[unique_key]

            if 'default_value' not in question_dict_key:
                question_to_tasks[unique_key]['default_value'] = defer_to_model

            if 'prompt' not in question_dict_key:
                question_to_tasks[unique_key]['prompt'] = 'Question'

            if 'type' not in question_dict_key:
                question_to_tasks[unique_key]['type'] = 'string'

            if 'models' not in question_dict_key:
                question_to_tasks[unique_key]['models'] = ['all']

            if 'ask_question' not in question_dict_key:
                question_to_tasks[unique_key]['ask_question'] = True


        else:
            question_to_tasks[unique_key] = {}
            question_to_tasks[unique_key]['default_value'] = defer_to_model
            question_to_tasks[unique_key]['options'] = defer_to_model
            question_to_tasks[unique_key]['prompt'] = 'Question'
            question_to_tasks[unique_key]['type'] = 'string'
            question_to_tasks[unique_key]['models'] = ['all']
            question_to_tasks[unique_key]['ask_question'] = True

        # Regardless of whether question was already in dictionary
        question_to_tasks[unique_key]['tasks'] = tasks

        outfile.write(yaml.dump(question_to_tasks, default_flow_style=False))
        outfile.write('\n')

    outfile.close()


# --------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    main()


# --------------------------------------------------------------------------------------------------
