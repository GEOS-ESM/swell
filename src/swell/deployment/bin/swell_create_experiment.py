#!/usr/bin/env python

# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import click
import os
import shutil
import yaml

from swell.deployment.prep_config import prepare_config
from swell.deployment.prep_exp_dirs import copy_eva_files, copy_platform_files, \
                                           template_modules_file, create_modules_csh
from swell.deployment.prep_suite import prepare_cylc_suite_jinja2
from swell.swell_path import get_swell_path
from swell.utilities.dictionary import dict_get
from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.logger import Logger
from swell.utilities.welcome_message import write_welcome_message


# --------------------------------------------------------------------------------------------------


@click.command()
@click.option('-c', '--config', 'config', default=None, help='Path to configuration file for the ' +
              'experiment. If not passed questions will be presented for setting up an experiment.')
def main(config):

    # Welcome message
    # ---------------
    write_welcome_message('Create Experiment')

    # Create a logger
    # ---------------
    logger = Logger('SwellCreateExperiment')

    # Generate the configuration file
    # -------------------------------
    if config is None:
        config_file = prepare_config('cli', 'hofx', 'nccs_discover')
    else:
        config_file = config

    # Load experiment file
    # --------------------
    with open(config_file, 'r') as ymlfile:
        experiment_dict = yaml.safe_load(ymlfile)

    # Extract from the config
    # -----------------------
    experiment_id = dict_get(logger, experiment_dict, 'experiment_id')
    experiment_root = dict_get(logger, experiment_dict, 'experiment_root')
    platform = dict_get(logger, experiment_dict, 'platform', None)
    suite_to_run = dict_get(logger, experiment_dict, 'suite_to_run')
    model_components = dict_get(logger, experiment_dict, 'model_components', None)

    # Make the suite directory
    # ------------------------
    exp_path = os.path.join(experiment_root, experiment_id)
    exp_suite_path = os.path.join(exp_path, experiment_id+'-suite')
    os.makedirs(exp_suite_path, 0o755, exist_ok=True)

    # Copy experiment file to suite dir
    # ---------------------------------
    shutil.copyfile(config_file, os.path.join(exp_suite_path, 'experiment.yaml'))

    # Copy suite and platform files to experiment suite directory
    # -----------------------------------------------------------
    swell_suite_path = os.path.join(get_swell_path(), 'suites', suite_to_run)
    copy_platform_files(logger, exp_suite_path, platform)

    if model_components is not None:
        copy_eva_files(logger, swell_suite_path, exp_suite_path, model_components)

    # Set the swell paths in the modules file and create csh versions
    # ---------------------------------------------------------------
    template_modules_file(logger, experiment_dict, exp_suite_path)
    create_modules_csh(logger, exp_suite_path)

    # Set the jinja2 file for cylc
    # ----------------------------
    prepare_cylc_suite_jinja2(logger, swell_suite_path, exp_suite_path, experiment_dict)

    # Copy config directory to experiment
    # -----------------------------------
    src = os.path.join(get_swell_path(), 'configuration')
    dst = os.path.join(exp_path, 'configuration')
    if os.path.exists(dst) and os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns('*.py*', '*__*'))

    # Write out launch command for convenience
    # ----------------------------------------
    logger.info(' ')
    logger.info('  Experiment successfully installed. To launch experiment use: ')
    logger.info('  swell_launch_experiment --suite_path ' + exp_suite_path, False)
    logger.info(' ')


# --------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    main()


# --------------------------------------------------------------------------------------------------
