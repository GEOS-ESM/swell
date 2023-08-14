# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import copy
import datetime
import os
import importlib
import yaml

from swell.utilities.logger import Logger
from swell.swell_path import get_swell_path
from swell.utilities.dictionary import dict_get, add_comments_to_dictionary, dictionary_override


# --------------------------------------------------------------------------------------------------


def update_model_components(logger, experiment_dict, comment_dict):

    if 'models' in experiment_dict:
        model_components_wanted = copy.copy(experiment_dict['model_components'])
        model_components_actual = list(experiment_dict['models'].keys())

        # If models element of experiment dictionary contains anything not in
        # model_components_actual then remove it from model
        for model in model_components_actual:
            if model not in model_components_wanted:
                logger.info(f'Removing model {model} from model_components')
                del(experiment_dict['models'][model])
                # Loop over all elements of the comment dictionay and remove any redundant keys
                for key in list(comment_dict.keys()):
                    if 'models.'+model in key:
                        del(comment_dict[key])


# --------------------------------------------------------------------------------------------------


def prepare_config(method, suite, platform, override, test):

    # Create a logger
    # ---------------
    logger = Logger('SwellPrepSuiteConfig')

    # Starting point for configuration generation
    # -------------------------------------------
    config_file = os.path.join(get_swell_path(), 'suites', 'suite_questions.yaml')

    # Assert valid method
    # -------------------
    valid_tasks = ['defaults', 'cli']
    if method not in valid_tasks:
        logger.abort(f'In Suites constructor method \'{method}\' not one of the valid ' +
                     f'tasks {valid_tasks}')

    # Set the object that will be used to populate dictionary options
    # ---------------------------------------------------------------
    PrepUsing = getattr(importlib.import_module('swell.deployment.prep_config_'+method),
                        'PrepConfig'+method.capitalize())
    prep_using = PrepUsing(logger, config_file, suite, platform)

    # Call the config prep step
    # -------------------------
    prep_using.execute()

    # Copy the experiment dictionary
    # ------------------------------
    experiment_dict = prep_using.experiment_dict
    comment_dict = prep_using.comment_dict

    # Add the datetime to the dictionary
    # ----------------------------------
    experiment_dict['datetime_created'] = datetime.datetime.today().strftime("%Y%m%d_%H%M%SZ")
    comment_dict['datetime_created'] = 'Datetime this file was created (auto added)'

    # Add the model components to the dictionary
    # ------------------------------------------
    if 'models' in experiment_dict:
        experiment_dict['model_components'] = list(experiment_dict['models'].keys())
        comment_dict['model_components'] = 'List of models in this experiment'

    # Expand all environment vars in the dictionary
    # ---------------------------------------------
    experiment_dict_string = yaml.dump(experiment_dict, default_flow_style=False, sort_keys=False)
    experiment_dict_string = os.path.expandvars(experiment_dict_string)
    experiment_dict = yaml.safe_load(experiment_dict_string)

    # Point to a particular pre-existing dictionary used for testing
    # --------------------------------------------------------------
    if test is not None:

        # Method must be defaults if specifying test
        logger.assert_abort(method == 'defaults',
                            f'If specifying a test override, the input method must be \'defaults\'')

        # Set an override to the test file
        test_override_file = os.path.join(get_swell_path(), 'test', 'suite_tests', suite + '-' +
                                          test + '.yaml')

        # Check that the test file choice is valid
        logger.assert_abort(os.path.exists(test_override_file), f'Requested test \'{test}\' does ' +
                            f'not exist. Expected file is \'{test_override_file}\'')

        # Open the override file
        with open(test_override_file, 'r') as file:
            test_override_dict = yaml.safe_load(file)

        # Perform the override
        logger.info(f'Overriding the experiment dictionary using suite test \'{test}\'')
        dictionary_override(logger, experiment_dict, test_override_dict)

    # Update model components in case the test override changed which are turned on
    # -----------------------------------------------------------------------------
    update_model_components(logger, experiment_dict, comment_dict)

    # Optionally override dictionary values (only used when method is 'defaults')
    # -------------------------------------
    if override is not None:

        # Method must be defaults if specifying override
        logger.assert_abort(method == 'defaults',
                            f'If specifying an override, the input method must be \'defaults\'')

        with open(override, 'r') as file:
            override_dict = yaml.safe_load(file)

        logger.info(f'Overriding experiment dictionary settings using {override}')
        dictionary_override(logger, experiment_dict, override_dict)

    # Update model components in case the user override changed which are turned on
    # -----------------------------------------------------------------------------
    update_model_components(logger, experiment_dict, comment_dict)

    # Add comments to dictionary
    # --------------------------
    experiment_dict_string = yaml.dump(experiment_dict, default_flow_style=False, sort_keys=False)

    experiment_dict_string_comments = add_comments_to_dictionary(experiment_dict_string,
                                                                 comment_dict)

    # Dictionary file to write
    # ------------------------
    cwd = os.getcwd()
    experiment_id = dict_get(logger, experiment_dict, 'experiment_id')
    exp_dict_file = os.path.join(cwd, f'{experiment_id}.yaml')

    # Write dictionary to YAML file
    # -----------------------------
    with open(exp_dict_file, 'w') as file:
        file.write(experiment_dict_string_comments)
    logger.info(f'Prepared configuration file written to {exp_dict_file}', False)

    # Return path to dictionary file
    # ------------------------------
    return exp_dict_file


# --------------------------------------------------------------------------------------------------
