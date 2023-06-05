#!/usr/bin/env python

# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


# standard imports
import os
import yaml

# swell imports
from swell.swell_path import get_swell_path
from swell.utilities.logger import Logger


# --------------------------------------------------------------------------------------------------


def main():

    # Create a logger
    logger = Logger('ListOfTaskQuestions')

    # Output file
    task_questions_config = os.path.join(get_swell_path(), 'tasks', 'task_questions.yaml')

    # Read input file into dictionary
    if os.path.exists(task_questions_config):
        with open(task_questions_config, 'r') as ymlfile:
            questions_dict = yaml.safe_load(ymlfile)
    else:
        logger.abort(f'Did not fine the task questions dictionary at {task_questions_config}')

    # Generate list of jedi interfaces
    jedi_interfaces_path = os.path.join(get_swell_path(), 'configuration', 'jedi', 'interfaces')
    jedi_interfaces = [f.path for f in os.scandir(jedi_interfaces_path) if f.is_dir()]
    jedi_interfaces = list(filter(lambda jedi_interface: '__' not in jedi_interface,
                                  jedi_interfaces))
    jedi_interface_names = []
    for jedi_interface in jedi_interfaces:
        jedi_interface_names.append(os.path.basename(jedi_interface))

    # Loop over jedi interfaces
    for jedi_interface_name in jedi_interface_names:

        question_defaults_dict = os.path.join(jedi_interfaces_path, jedi_interface_name,
                                              'task_questions.yaml')

        # Open the existing file
        with open(question_defaults_dict, 'r') as ymlfile:
            question_dict_defaults_exist = yaml.safe_load(ymlfile)

        if question_dict_defaults_exist is None:
            question_dict_defaults_exist = {}

        # Open file ready to overwrite
        outfile = open(question_defaults_dict, 'w')

        # Loop over main question list
        for question_key, question_dict in questions_dict.items():

            # Check if question defers the default value to the jedi interface
            if question_dict['default_value'] == 'defer_to_model':

                # If default is deferred to model the dict must contain the jedi interface list
                logger.assert_abort('models' in question_dict, f'If the default for the config ' +
                                    f'is defer to model then the question dictionary must ' +
                                    f'contain models. Offending key: {question_key}')

                # Set the required jedi interfaces for this question
                jedi_int_needed = question_dict['models']
                if jedi_int_needed[0] == 'all' or jedi_interface_name in jedi_int_needed:

                    # Create dictionary if it does not already exist
                    if question_key not in question_dict_defaults_exist:

                        # Create defaults dictionary for the question
                        question_dict_defaults = {question_key: {
                           'default_value': 'defer_to_model'
                        }}

                        if 'options' in question_dict:
                            question_dict_defaults[question_key]['options'] = ['defer_to_model']

                    else:

                        # Copy from the existing dictionary
                        question_dict_defaults = {
                            question_key: question_dict_defaults_exist[question_key]
                            }

                    # Write to the YAML file
                    outfile.write(yaml.dump(question_dict_defaults, default_flow_style=False))
                    outfile.write('\n')

    # Generate list of platforms
    platforms_path = os.path.join(get_swell_path(), 'deployment', 'platforms')
    platforms = [f.path for f in os.scandir(platforms_path) if f.is_dir()]
    platforms = list(filter(lambda platform: '__' not in platform, platforms))
    platform_names = []
    for platform in platforms:
        platform_names.append(os.path.basename(platform))

    # Loop over platforms
    for platform_name in platform_names:

        question_defaults_dict = os.path.join(platforms_path, platform_name,
                                              'task_questions.yaml')

        # Open the existing file
        with open(question_defaults_dict, 'r') as ymlfile:
            question_dict_defaults_exist = yaml.safe_load(ymlfile)

        if question_dict_defaults_exist is None:
            question_dict_defaults_exist = {}

        # Open file ready to overwrite
        outfile = open(question_defaults_dict, 'w')

        # Loop over main question list
        for question_key, question_dict in questions_dict.items():

            # Check if question defers the default value to the platform
            if question_dict['default_value'] == 'defer_to_platform':

                # Create dictionary if it does not already exist
                if question_key not in question_dict_defaults_exist:

                    # Create defaults dictionary for the question
                    question_dict_defaults = {question_key: {
                           'default_value': 'defer_to_model'
                    }}

                    if 'options' in question_dict:
                        question_dict_defaults[question_key]['options'] = ['defer_to_model']

                else:

                    # Copy from the existing dictionary
                    question_dict_defaults = {
                        question_key: question_dict_defaults_exist[question_key]
                        }

                # Write to the YAML file
                outfile.write(yaml.dump(question_dict_defaults, default_flow_style=False))
                outfile.write('\n')


# --------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    main()


# --------------------------------------------------------------------------------------------------
