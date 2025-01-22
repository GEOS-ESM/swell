# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


# standard imports
import glob
import os
import random
import string
import yaml

# swell imports
from swell.swell_path import get_swell_path
from swell.utilities.logger import Logger
from swell.utilities.case_switching import snake_case_to_camel_case


# --------------------------------------------------------------------------------------------------


def tq_dicts(tempdir: str):

    # Create a logger
    logger = Logger('ListOfTaskQuestions')

    # All python files
    task_codes = glob.glob(os.path.join(get_swell_path(), 'tasks', '*.py'))
    task_codes = list(filter(lambda task_code: task_code != '__init__.py', task_codes))

    # Target YAML file
    destination_yaml = os.path.join(get_swell_path(), 'tasks', 'task_questions.yaml')

    # Print message
    logger.info(f'Running tool to regenerate the task questions dictionary. Output dictionary ' +
                f'be written to {destination_yaml}')

    # Read input file into dictionary
    if os.path.exists(destination_yaml):
        with open(destination_yaml, 'r') as ymlfile:
            question_dict_str = ymlfile.read()
        question_dict = yaml.safe_load(question_dict_str)
    else:
        question_dict = {}
        question_dict_str = ''

    question_dict_str_in = question_dict_str

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

    # Create string with new dictionary
    dict_to_write_str = ''
    for key, value in question_to_tasks.items():
        # Create dictionary one at a time and write
        dict_to_write = {}
        dict_to_write[key] = value
        dict_to_write_str = dict_to_write_str + yaml.dump(dict_to_write, default_flow_style=False)
        dict_to_write_str = dict_to_write_str + '\n'

    # Check whether the string of the new dictionary matches the existing one.
    if dict_to_write_str == question_dict_str_in:

        logger.info(f'The code will make no change to the task questions dictionary. Clean exit')
        return 0

    else:

        # Write the new dictionary to a temporary file
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        destination_yaml_temp = os.path.join(tempdir, f'task_questions_{random_string}.yaml')

        with open(destination_yaml_temp, 'w') as file:
            file.write(dict_to_write_str)

        logger.info(f'If a new \'task_questions.yaml\' is generated using this utility the ' +
                    f'resulting file will be different. This could be for a number of reasons:')
        logger.info(f' ', False)
        logger.info(f'  - Comments were added to the original file.')
        logger.info(f'  - A new key is accessed from a task.')
        logger.info(f'  - Referencing of a particular key has been removed from a task.')
        logger.info(f' ', False)
        logger.info(f'Please compare the new (temporary) file \'{destination_yaml_temp}\' with ' +
                    f'the existing file: \'tasks/task_questions.yaml\' and resolve differences.')

        return 1


# --------------------------------------------------------------------------------------------------
