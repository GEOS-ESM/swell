# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import datetime
import os
import importlib
import ruamel.yaml as ry
import sys
import yaml

from swell.utilities.logger import Logger
from swell.swell_path import get_swell_path
from swell.utilities.dictionary import dict_get, add_comments_to_dictionary
from swell.utilities.jinja2 import template_string_jinja2


# --------------------------------------------------------------------------------------------------


def platform_fill(logger, experiment_dict, ci_cd, comment_dict):

    # Get platform
    platform = experiment_dict['platform']

    # Open platform experiment.yaml
    platform_exp_file = os.path.join(get_swell_path(), 'deployment', 'platforms', platform,
                                     'experiment.yaml')

    with open(platform_exp_file, 'r') as platform_exp_file_open:
        platform_exp_templated = platform_exp_file_open.read()

    # Create a template dictionary
    temp_experiment_dict = experiment_dict
    temp_experiment_dict['datetime'] = datetime.datetime.today().strftime("%Y%m%d_%H%M%SZ")

    # Resolve any templates
    platform_exp_str = template_string_jinja2(logger, platform_exp_templated, temp_experiment_dict)

    # Load to dictionary
    platform_dict = yaml.safe_load(platform_exp_str)

    # Set platform dictionary to use
    dict_to_use = 'default'
    if ci_cd:
        dict_to_use = 'ci_cd'

        # Ensure environment variables are set
        logger.assert_abort(os.environ.get('CICD_EXPERIMENT_ID') is not None,
                            'If running with CI/CD the environment variable ' +
                            '${CICD_EXPERIMENT_ID} must be set.')
        logger.assert_abort(os.environ.get('CICD_EXPERIMENT_ROOT') is not None,
                            'If running with CI/CD the environment variable ' +
                            '${CICD_EXPERIMENT_ROOT} must be set.')

    # Update experiment dict
    experiment_dict_new = experiment_dict
    experiment_dict_new['experiment_id'] = platform_dict[dict_to_use]['experiment_id']
    experiment_dict_new['experiment_root'] = platform_dict[dict_to_use]['experiment_root']

    # Add the swell static files path from the platform to the experiment dictionary
    experiment_dict_new['swell_static_files'] = platform_dict['default']['swell_static_files']

    # Adjust comment dictionary
    comment_dict_new = comment_dict
    comment_dict_new['datetime'] = 'Datetime this file was created (auto added)'
    comment_dict_new['swell_static_files'] = 'Path to static files needed by swell (auto added)'

    return experiment_dict_new, comment_dict_new


# --------------------------------------------------------------------------------------------------


def prepare_config(method, ci_cd=False):

    # Create a logger
    # ---------------
    logger = Logger('SwellPrepSuiteConfig')

    # Starting point for configuration generation
    # -------------------------------------------
    config_file = os.path.join(get_swell_path(), 'suites', 'suites.yaml')

    # Assert valid method
    # -------------------
    valid_tasks = ['defaults', 'gui', 'cli']
    if method not in valid_tasks:
        logger.abort(f'In Suites constructor method \'{method}\' not one of the valid ' +
                     f'tasks {valid_tasks}')

    # Set the object that will be used to populate dictionary options
    # ---------------------------------------------------------------
    PrepUsing = getattr(importlib.import_module('swell.deployment.prep_config_'+method),
                        'PrepConfig'+method.capitalize())
    prep_using = PrepUsing(logger, config_file)

    # Call the config prep step
    # -------------------------
    prep_using.execute()

    # Set platform specific entires
    # -----------------------------
    experiment_dict, comment_dict = platform_fill(logger, prep_using.experiment_dict, ci_cd,
                                                  prep_using.comment_dict)

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

    # Dictionary file to write
    # ------------------------
    cwd = os.getcwd()
    experiment_id = dict_get(logger, experiment_dict, 'experiment_id')
    exp_dict_file = os.path.join(cwd, f'experiment-{experiment_id}.yaml')

    # Write dictionary to YAML file
    # -----------------------------
    exp_dict_file_open = open(exp_dict_file, "w")
    n = exp_dict_file_open.write(experiment_dict_string_comments)
    exp_dict_file_open.close()
    logger.info(f'Prepared configuration file written to {exp_dict_file}', False)

    # Return path to dictionary file
    # ------------------------------
    return exp_dict_file


# --------------------------------------------------------------------------------------------------
