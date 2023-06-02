#!/usr/bin/env python

# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


# standard imports
import glob
import os
import yaml

# swell imports
from swell.swell_path import get_swell_path
from swell.utilities.logger import Logger
from swell.utilities.case_switching import snake_case_to_camel_case


# --------------------------------------------------------------------------------------------------


def main(test_mode):

    # Create a logger
    logger = Logger('ListOfTaskQuestions')

    # Path to JEDI interface code
    swell_path = get_swell_path()

    # All python files
    task_codes = glob.glob(os.path.join(get_swell_path(), 'tasks', '*.py'))
    task_codes = list(filter(lambda task_code: task_code != '__init__.py', task_codes))

    # Target YAML file
    destination_yaml = os.path.join(get_swell_path(), 'tasks', 'task_questions.yaml')

    # Read input file into dictionary
    if os.path.exists(destination_yaml):
        with open(destination_yaml, 'r') as ymlfile:
            question_dict = yaml.safe_load(ymlfile)
    else:
        question_dict = {}

    question_dict_in = question_dict.copy()

    # Now safe to overwrite file
    outfile = open(destination_yaml, 'w')

    # Loop through task code and accumulate all lines containing a use of config
    config_keys = []
    task_names = []
    for task_code in task_codes:

        # Open code for this task
        with open(task_code, 'r') as file:

            # Loop over lines and append if line contains
            for file_line in file.read().split('\n'):
                if 'self.config.' in file_line:

                    config_key = file_line.split('self.config.')[1].split('(')[0].strip()
                    task_name = os.path.basename(str(task_code)).split('.')[0]
                    task_name = snake_case_to_camel_case(task_name)

                    config_keys.append(config_key)
                    task_names.append(task_name)

    # For each key create lists of tasks
    unique_keys = sorted(list(set(config_keys)))

    # question to task dictionary
    question_to_tasks = {}

    # Task for each key
    for unique_key in unique_keys:

        tasks = []

        for task_name, config_key in zip(task_names, config_keys):

            if unique_key == config_key:

                tasks.append(task_name)

        # Make sure tasks are unique
        tasks = sorted(list(set(tasks)))

        # Create dictionary to hold question components
        question_to_tasks = {}

        if unique_key in question_dict:

            question_to_tasks[unique_key] = question_dict[unique_key]

            question_dict_key = question_dict[unique_key]

            # Make sure minimal things are in the question's dictionary
            if 'default_value' not in question_dict_key:
                question_to_tasks[unique_key]['default_value'] = 'defer_to_model'

            if 'prompt' not in question_dict_key:
                question_to_tasks[unique_key]['prompt'] = 'Question'

            if 'type' not in question_dict_key:
                question_to_tasks[unique_key]['type'] = 'string'

            if 'ask_question' not in question_dict_key:
                question_to_tasks[unique_key]['ask_question'] = True

        else:

            question_to_tasks[unique_key] = {}
            question_to_tasks[unique_key]['default_value'] = 'defer_to_model'
            question_to_tasks[unique_key]['options'] = 'defer_to_model'
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
