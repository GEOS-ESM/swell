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
@click.argument('config_file')
def main(config_file):

    # Welcome message
    # ---------------
    write_welcome_message('Create Experiment')

    # Create a logger
    # ---------------
    logger = Logger('SwellCreateExperiment')

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

    if os.path.exists(os.path.join(swell_suite_path, 'eva')):
        copy_eva_files(logger, swell_suite_path, exp_suite_path)

    # Create R2D2 database file
    # -------------------------
    r2d2_local_path = dict_get(logger, experiment_dict, 'r2d2_local_path', None)
    if r2d2_local_path is not None:
        r2d2_conf_path = os.path.join(exp_suite_path, 'r2d2_config.yaml')

        # Write R2D2_CONFIG to modules
        with open(os.path.join(exp_suite_path, 'modules'), 'a') as module_file:
            module_file.write(f'export R2D2_CONFIG={r2d2_conf_path}')

        # Open the r2d2 file to dictionary
        with open(r2d2_conf_path, 'r') as r2d2_file_open:
            r2d2_file_str = r2d2_file_open.read()
        r2d2_file_str = template_string_jinja2(logger, r2d2_file_str, experiment_dict)
        r2d2_file_str = os.path.expandvars(r2d2_file_str)

        with open(r2d2_conf_path, 'w') as r2d2_file_open:
            r2d2_file_open.write(r2d2_file_str)

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
