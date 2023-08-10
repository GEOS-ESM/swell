# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import datetime
import os
import importlib
import yaml

from swell.utilities.logger import Logger
from swell.swell_path import get_swell_path
from swell.utilities.dictionary import dict_get, add_comments_to_dictionary, dictionary_override


# --------------------------------------------------------------------------------------------------


def prepare_config(method, suite, platform, override):

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

    # Optionally override dictionary values (only used when method is 'defaults')
    # -------------------------------------
    if method == 'defaults' and override is not None:
        dictionary_override(logger, experiment_dict, override)

    # Add comments to dictionary
    # --------------------------
    experiment_dict_string = yaml.dump(experiment_dict, default_flow_style=None, sort_keys=False)

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
