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
from swell.utilities.dictionary import dict_get, add_comments_to_dictionary


# --------------------------------------------------------------------------------------------------


def update_model_components(logger, experiment_dict, comment_dict):

    if 'models' in experiment_dict:
        model_components_wanted = copy.copy(experiment_dict['model_components'])
        model_components_actual = list(experiment_dict['models'].keys())

        # If models element of experiment dictionary contains anything not in
        # model_components_actual then remove it from model
        for model in model_components_actual:
            if model not in model_components_wanted:
                del (experiment_dict['models'][model])
                # Loop over all elements of the comment dictionay and remove any redundant keys
                for key in list(comment_dict.keys()):
                    if 'models.'+model in key:
                        del (comment_dict[key])


# --------------------------------------------------------------------------------------------------


def clone_config(configuration, experiment_id, method, platform, advanced):

    # Create a logger
    logger = Logger('SwellCloneExperiment')

    # Check that configuration exists and is a YAML file
    if not os.path.isfile(configuration):
        logger.abort(f'The provided configuration file {configuration} does not exist')

    # Open the target experiment YAML. It will be used as the override
    with open(configuration, 'r') as f:
        override_dict = yaml.safe_load(f)

    # Check that override_dict has a suite key and get the suite name
    if 'suite_to_run' not in override_dict:
        logger.abort('The provided configuration file does not have a \'suite_to_run\' key')
    suite = override_dict['suite_to_run']

    # The user may want to run on a different platform (if so adjust the override)
    if platform is not None:
        override_dict['platform'] = platform

    # Set the experiment_id in the override dictionary
    override_dict['experiment_id'] = experiment_id

    # First create the configuration for the experiment.
    return prepare_config(suite, method, override_dict['platform'], override_dict, advanced)


# --------------------------------------------------------------------------------------------------


def prepare_config(suite, method, platform, override, advanced):

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
    prep_using = PrepUsing(logger, config_file, suite, platform, override, advanced)

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

    # Add comments to dictionary
    # --------------------------
    experiment_dict_string = yaml.dump(experiment_dict, default_flow_style=False, sort_keys=False)

    experiment_dict_string_comments = add_comments_to_dictionary(experiment_dict_string,
                                                                 comment_dict)

    # Return path to dictionary file
    # ------------------------------
    return experiment_dict_string_comments


# --------------------------------------------------------------------------------------------------
