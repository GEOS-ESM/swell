# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import importlib
import ruamel.yaml as ry
import sys
import yaml

from swell.utilities.logger import Logger
from swell.swell_path import get_swell_path
from swell.utilities.dictionary_utilities import get_element, add_comments_to_dictionary

# --------------------------------------------------------------------------------------------------


def prepare_config(method):

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

    # Write final experiment dictionary
    # ---------------------------------
    experiment_id = get_element(logger, prep_using.experiment_dict, 'experiment_id')
    experiment_rt = get_element(logger, prep_using.experiment_dict, 'experiment_root')

    experiment_rt = os.path.expandvars(experiment_rt)
    prep_using.experiment_dict['experiment_root'] = experiment_rt

    # Make directory
    # --------------
    experiment_root_id = os.path.join(experiment_rt, experiment_id)
    os.makedirs(experiment_root_id, exist_ok=True)

    # Add comments to dictionary
    # --------------------------
    experiment_dict_string = yaml.dump(prep_using.experiment_dict,
                                       default_flow_style=False, sort_keys=False)

    experiment_dict_string_comments = add_comments_to_dictionary(experiment_dict_string,
                                                                 prep_using.comment_dict)

    # Dictionary file to write
    exp_dict_file = os.path.join(experiment_root_id, 'experiment.yaml')

    # Write dictionary to YAML file
    exp_dict_file_open = open(exp_dict_file, "w")
    n = exp_dict_file_open.write(experiment_dict_string_comments)
    exp_dict_file_open.close()
    logger.info(f'Prepared configuration file written to {exp_dict_file}')

    return exp_dict_file


# --------------------------------------------------------------------------------------------------
