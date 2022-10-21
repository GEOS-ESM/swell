#!/usr/bin/env python

# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import argparse
import os
import shutil
import yaml

from swell.swell_path import get_swell_path
from swell.utilities.logger import Logger
from swell.utilities.string_utils import replace_vars
from swell.utilities.dictionary_utilities import dict_get
from swell.deployment.prep_exp_dirs import copy_suite_and_platform_files, \
                                           set_swell_path_in_modules, create_modules_csh
from swell.deployment.prep_suite import prepare_cylc_suite_jinja2


# --------------------------------------------------------------------------------------------------


def main():

    # Arguments
    # ---------
    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=str, help='Configuration file with experiment options.')

    args = parser.parse_args()
    config = args.config

    # Create a logger
    # ---------------
    logger = Logger('SwellCreateExperiment')

    # Load experiment file
    # --------------------
    with open(config, 'r') as ymlfile:
        experiment_dict = yaml.safe_load(ymlfile)

    # Extract from the config
    # -----------------------
    experiment_id = dict_get(logger, experiment_dict, 'experiment_id')
    experiment_root = dict_get(logger, experiment_dict, 'experiment_root')
    platform = dict_get(logger, experiment_dict, 'platform', None)
    suite_to_run = dict_get(logger, experiment_dict, 'suite_to_run')
    model_components = dict_get(logger, experiment_dict, 'model_components')

    # Make the suite directory
    # ------------------------
    exp_suite_path = os.path.join(experiment_root, experiment_id, experiment_id+'-suite')
    os.makedirs(exp_suite_path, 0o755, exist_ok=True)

    # Copy experiment file to suite dir
    # ---------------------------------
    shutil.copyfile(config, os.path.join(exp_suite_path, 'experiment.yaml'))

    # Copy suite and platform files to experiment suite directory
    # -----------------------------------------------------------
    swell_suite_path = os.path.join(get_swell_path(), 'suites', suite_to_run)
    copy_suite_and_platform_files(logger, swell_suite_path, exp_suite_path, platform)

    # Create R2D2 database file
    # -------------------------
    r2d2_conf_path = os.path.join(exp_suite_path, 'r2d2_config.yaml')

    # Write R2D2_CONFIG to modules
    with open(os.path.join(exp_suite_path, 'modules'), 'a') as module_file:
        module_file.write(f'export R2D2_CONFIG={r2d2_conf_path}')

    # Open the r2d2 file to dictionary
    with open(r2d2_conf_path, 'r') as r2d2_file_open:
        r2d2_file_str = r2d2_file_open.read()
    r2d2_file_str = replace_vars(r2d2_file_str, **experiment_dict)
    r2d2_file_str = os.path.expandvars(r2d2_file_str)

    with open(r2d2_conf_path, 'w') as r2d2_file_open:
        r2d2_file_open.write(r2d2_file_str)

    # Set the swell paths in the modules file and create csh versions
    # ---------------------------------------------------------------
    set_swell_path_in_modules(logger, exp_suite_path)
    create_modules_csh(logger, exp_suite_path)

    # Set the jinja2 file for cylc
    # ----------------------------
    prepare_cylc_suite_jinja2(logger, swell_suite_path, exp_suite_path, experiment_dict)

    # Write out launch command for convenience
    # ----------------------------------------
    logger.info(' ')
    logger.info('  Experiment successfully installed. To launch experiment use: ')
    logger.info('  swell_launch_experiment --suite_path ' + exp_suite_path)
    logger.info(' ')


# --------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    main()


# --------------------------------------------------------------------------------------------------
