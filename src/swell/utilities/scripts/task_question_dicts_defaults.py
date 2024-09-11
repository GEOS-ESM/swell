# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


# standard imports
import os
import random
import string
import yaml
from typing import Union

# swell imports
from swell.swell_path import get_swell_path
from swell.utilities.logger import Logger


# --------------------------------------------------------------------------------------------------


def create_jedi_tq_dicts(
    logger: 'Logger',
    jedi_interface_name: str,
    tq_dicts: Union[list, dict],
    jedi_tq_dicts_str_in: str
) -> str:

    # Convert string read from file to dictionary
    if jedi_tq_dicts_str_in == '':
        jedi_tq_dicts = {}
    else:
        jedi_tq_dicts = yaml.safe_load(jedi_tq_dicts_str_in)

    # Create string that will hold the new dictionaries
    jedi_tq_dicts_str = ''

    # Loop over main question list
    for tq, tq_dict in tq_dicts.items():

        # Check if question defers the default value to the jedi interface
        if tq_dict['default_value'] == 'defer_to_model':

            # If default is deferred to model the dict must contain the jedi interface list
            logger.assert_abort('models' in tq_dict, f'If the default for the config is ' +
                                f'\'defer_to_model\' then the question dictionary must ' +
                                f'contain \'models\'. Offending task question: {tq}')

            # Set the required jedi interfaces for this question
            jedi_int_needed = tq_dict['models']

            # This tq is only added if this model in question can provide that config
            if jedi_int_needed[0] == 'all' or jedi_interface_name in jedi_int_needed:

                # Create dictionary to hold this task question
                jedi_tq_dict = {tq: {}}

                # Create dictionary if it does not already exist
                if tq not in jedi_tq_dicts:

                    # Create defaults dictionary for the question
                    jedi_tq_dict[tq]['default_value'] = ['defer_to_model']

                    if 'options' in tq_dict:
                        jedi_tq_dict[tq]['options'] = ['defer_to_model']

                else:

                    # Copy from the existing dictionary
                    jedi_tq_dict[tq] = jedi_tq_dicts[tq]

                # Add dictionary to the output dictionary
                jedi_tq_dicts_str = jedi_tq_dicts_str + yaml.dump(jedi_tq_dict,
                                                                  default_flow_style=False)
                jedi_tq_dicts_str = jedi_tq_dicts_str + '\n'

    # Return dictionary in string format
    return jedi_tq_dicts_str


# --------------------------------------------------------------------------------------------------


def create_platform_tq_dicts(
    logger: 'Logger',
    platform_name: str,
    tq_dicts: Union[list, dict],
    platform_tq_dicts_str_in: str
) -> str:

    # Convert string read from file to dictionary
    if platform_tq_dicts_str_in == '':
        platform_tq_dicts = {}
    else:
        platform_tq_dicts = yaml.safe_load(platform_tq_dicts_str_in)

    # Create string that will hold the new dictionaries
    platform_tq_dicts_str = ''

    # Loop over main question list
    for tq, tq_dict in tq_dicts.items():

        # Check if question defers the default value to the platform
        if tq_dict['default_value'] == 'defer_to_platform':

            # Create dictionary to hold this task question
            platform_tq_dict = {tq: {}}

            # Create dictionary if it does not already exist
            if tq not in platform_tq_dicts:

                # Create defaults dictionary for the question
                platform_tq_dict[tq]['default_value'] = ['defer_to_model']

                if 'options' in tq_dict:
                    platform_tq_dict[tq]['options'] = ['defer_to_model']

            else:

                # Copy from the existing dictionary
                platform_tq_dict[tq] = platform_tq_dicts[tq]

            # Add dictionary to the output dictionary
            platform_tq_dicts_str = platform_tq_dicts_str + yaml.dump(platform_tq_dict,
                                                                      default_flow_style=False)
            platform_tq_dicts_str = platform_tq_dicts_str + '\n'

    # Return dictionary in string format
    return platform_tq_dicts_str


# --------------------------------------------------------------------------------------------------


def main() -> int:

    # Create a logger
    logger = Logger('ListOfTaskQuestions')

    # Output file
    task_questions_config = os.path.join(get_swell_path(), 'tasks', 'task_questions.yaml')

    # Read input file into dictionary
    if os.path.exists(task_questions_config):
        with open(task_questions_config, 'r') as ymlfile:
            tq_dicts = yaml.safe_load(ymlfile)
    else:
        logger.abort(f'Did not fine the task questions dictionary at {task_questions_config}')

    # Generate list of JEDI interfaces
    # --------------------------------
    jedi_interfaces_path = os.path.join(get_swell_path(), 'configuration', 'jedi', 'interfaces')
    jedi_interfaces = [f.path for f in os.scandir(jedi_interfaces_path) if f.is_dir()]
    jedi_interfaces = list(filter(lambda jedi_interface: '__' not in jedi_interface,
                                  jedi_interfaces))
    jedi_interface_names = []
    jedi_interface_paths = []
    for jedi_interface in jedi_interfaces:
        jedi_interface_names.append(os.path.basename(jedi_interface))
        jedi_interface_paths.append(os.path.join(jedi_interfaces_path, jedi_interface_names[-1],
                                                 'task_questions.yaml'))

    # Generate list of platforms
    # --------------------------
    platforms_path = os.path.join(get_swell_path(), 'deployment', 'platforms')
    platforms = [f.path for f in os.scandir(platforms_path) if f.is_dir()]
    platforms = list(filter(lambda platform: '__' not in platform, platforms))
    platform_names = []
    platform_paths = []
    for platform in platforms:
        platform_names.append(os.path.basename(platform))
        platform_paths.append(os.path.join(platforms_path, platform_names[-1],
                                           'task_questions.yaml'))

    # Loop over jedi interfaces and platforms and create dictionaries
    # ---------------------------------------------------------------
    # Combine jedi and platforms
    tq_dicts_names = jedi_interface_names + platform_names
    tq_dicts_paths = jedi_interface_paths + platform_paths

    # Record whether anything failed
    failure = 0

    for tq_dicts_name, tq_dicts_path in zip(tq_dicts_names, tq_dicts_paths):

        logger.info(f'Processing defaults dictionary for \'{tq_dicts_name}\'')

        # Open the existing file
        if os.path.exists(tq_dicts_path):
            with open(tq_dicts_path, 'r') as file:
                dicts_str_in = file.read()
        else:
            dicts_str_in = ''

        # Create a new dictionary for this interface
        if tq_dicts_name in jedi_interface_names:
            tq_dicts_str = create_jedi_tq_dicts(logger, tq_dicts_name, tq_dicts, dicts_str_in)
        elif tq_dicts_name in platform_names:
            tq_dicts_str = create_platform_tq_dicts(logger, tq_dicts_name, tq_dicts, dicts_str_in)

        # Perform comparison of input and output and write temporaries if needed

        # Check whether the string of the new dictionary matches the existing one.
        if tq_dicts_str == dicts_str_in:

            logger.info(f'The code will make no change to the task questions dictionary.')

        if tq_dicts_str != dicts_str_in or 'defer_to_' in tq_dicts_str:

            # Write the new dictionary to a temporary file
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            temp_tq_file_name = f'{tq_dicts_name}_task_questions_{random_string}.yaml'
            destination_yaml_temp = os.path.join('/tmp', temp_tq_file_name)

            with open(destination_yaml_temp, 'w') as file:
                file.write(tq_dicts_str)

            # If there is a dictionary mismatch inform the user
            if tq_dicts_str != dicts_str_in:

                logger.info(f'If a new \'task_questions.yaml\' is generated for ' +
                            f'\'{tq_dicts_name}\' using this utility the resulting file will be ' +
                            f'different. This could be for a number of reasons:')
                logger.info(f' ', False)
                logger.info(f'  - Comments were added to the original file.')
                logger.info(f'  - A new key is accessed from a task.')
                logger.info(f'  - Referencing of a particular key has been removed from a task.')
                logger.info(f' ', False)
                logger.info(f'Please compare the new (temporary) file \'{destination_yaml_temp}\'' +
                            f' with the existing file: \'{tq_dicts_name}/task_questions.yaml\' ' +
                            f'and resolve the differences')

            # If there is a defer to in the file still then inform user
            if 'defer_to_' in tq_dicts_str:

                logger.info(f'The dictionary that was created for \'{tq_dicts_name}\' contains ' +
                            f'\'defer_to_\'. Ensure these instances are resolved when comparing ' +
                            f'the new (temporary) file \'{destination_yaml_temp}\' with the ' +
                            f'existing file: \'{tq_dicts_name}/task_questions.yaml\' and resolve ' +
                            f'the differences. Once resolved rerun this utility to ensure tests ' +
                            f'pass.')

            # Uptick failure count
            failure = failure + 1

        # Crete a space between loop elements
        logger.info(' ', False)

    # Return code
    if failure > 0:
        return 1
    else:
        return 0


# --------------------------------------------------------------------------------------------------
