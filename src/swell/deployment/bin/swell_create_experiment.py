#!/usr/bin/env python

# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
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
from swell.deployment.prep_exp_dirs import copy_suite_and_platform_files, \
                                           set_swell_path_in_modules, create_modules_csh
from swell.deployment.prep_suite import prepare_cylc_suite_jinja2
from swell.swell_path import get_swell_path
from swell.utilities.dictionary_utilities import dict_get
from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.logger import Logger


# --------------------------------------------------------------------------------------------------


@click.command()
@click.option('-m', '--method', 'method', default='defaults',
              help='Method for configuration: [\'defaults\'], \'tui\' or \'existing\'. If using ' +
                   '\'existing\' then the config argument must also be passed proving path to ' +
                   'config.')
@click.option('-c', '--config', 'config', default=None,
              help='Directory containing the suite file needed by the workflow manager')
@click.option('-t', '--cidi', 'ci_cd', default=False,
              help='Setup experiment using continuous integration parameters')
def main(method, config, ci_cd):

    # Create a logger
    # ---------------
    logger = Logger('SwellCreateExperiment')

    # Check arguments
    # ---------------
    method_options = ['defaults', 'tui', 'existing']
    logger.assert_abort(method in method_options, f'Method \'{method}\' is not one of the valid ' +
                        f'options {method_options}.')
    if method == 'existing':
        logger.assert_abort(config is not None, f'If method is \'existing\' config path must be ' +
                            f'present in the list of arguments')

    # Generate the configuration file
    # -------------------------------
    if method != 'existing':
        config_file = prepare_config(method, ci_cd)
    else:
        config_file = config

    # Load experiment file
    # --------------------
    with open(config_file, 'r') as ymlfile:
        experiment_dict = yaml.safe_load(ymlfile)

    exit()

    # Extract from the config
    # -----------------------
    experiment_id = dict_get(logger, experiment_dict, 'experiment_id')
    experiment_root = dict_get(logger, experiment_dict, 'experiment_root')
    platform = dict_get(logger, experiment_dict, 'platform', None)
    suite_to_run = dict_get(logger, experiment_dict, 'suite_to_run')
    model_components = dict_get(logger, experiment_dict, 'model_components')

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
    r2d2_file_str = template_string_jinja2(logger, r2d2_file_str, experiment_dict)
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
