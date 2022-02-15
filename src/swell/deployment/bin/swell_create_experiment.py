#!/usr/bin/env python

# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import click
import os
import shutil
import yaml

from swell.install_path import swell_install_path
from swell.utilities.logger import Logger
from swell.utilities.git_utils import git_got
from swell.utilities.dictionary_utilities import resolve_definitions
from swell.deployment.prep_exp_dirs import add_dir_to_conf_mkdir, copy_suite_files
from swell.deployment.yaml_exploder import recursive_yaml_expansion
from swell.deployment.prep_suite import prepare_suite


# --------------------------------------------------------------------------------------------------


@click.command()
@click.argument('config')
@click.option('--clean', '-c', is_flag=True, help='Remove any existing experiment directory')
def main(config, clean):

    # Create a logger
    # ---------------
    logger = Logger('SwellCreateExperiment')

    # Load experiment file
    # --------------------
    with open(config, 'r') as ymlfile:
        experiment_dict = yaml.safe_load(ymlfile)

    # Set experiment directory
    # ------------------------
    exp_root = experiment_dict['experiment_root'].replace('${USER}', os.environ['USER'])
    exp_id = experiment_dict['experiment_id']
    experiment_dir = os.path.join(exp_root, exp_id)

    # Add to dictionary
    experiment_dict.update({'experiment_dir': experiment_dir})

    # Optionally clean up any existing directory
    # ------------------------------------------
    if clean:
        logger.input('Removing existing experiment directory ' + experiment_dir)
        logger.info('removing' + experiment_dir)
        shutil.rmtree(experiment_dir)

    # Create the experiment directory
    # -------------------------------
    logger.info('Creating experiment directory: '+experiment_dir)
    if not os.path.exists(experiment_dir):
        os.makedirs(experiment_dir, 0o755)
    else:
        logger.info('Experiment directory is already present, overwriting files')

    # Copy experiment.yaml to the experiment directory with the experiment id name
    # ----------------------------------------------------------------------------
    shutil.copy(config, os.path.join(experiment_dir, 'experiment_{}.yaml'.format(exp_id)))
    logger.info('Experiment yaml copied to working directory...')

    # Create directories within experiment directory and add key to dictionary
    # ------------------------------------------------------------------------
    add_dir_to_conf_mkdir(logger, experiment_dict, 'bundle_dir', 'bundle')
    add_dir_to_conf_mkdir(logger, experiment_dict, 'jedi_build_dir', 'bundle/build', False)
    add_dir_to_conf_mkdir(logger, experiment_dict, 'stage_dir', 'stage')
    add_dir_to_conf_mkdir(logger, experiment_dict, 'suite_dir', exp_id+'-suite')
    add_dir_to_conf_mkdir(logger, experiment_dict, 'run_dir', 'run')
    add_dir_to_conf_mkdir(logger, experiment_dict, 'cycle_dir', 'run/{{current_cycle}}', False)

    # Put the swell install path in to the config
    # -------------------------------------------
    swell_dir = swell_install_path()
    add_dir_to_conf_mkdir(logger, experiment_dict, 'swell_dir', swell_dir, False)

    # Resolve all dictionary definitions
    # ----------------------------------
    experiment_dict = resolve_definitions(experiment_dict)

    # Copy files to the suite directory
    # ---------------------------------
    copy_suite_files(logger, experiment_dict)

    # Clone the git repos needed for the yaml file explosion
    # ------------------------------------------------------
    # User chosen clones
    needed_repos = []
    bundle_repos = experiment_dict['build jedi']['bundle repos']
    for bundle_repo in bundle_repos:
        if 'clone on create' in bundle_repo.keys():
            if bundle_repo['clone on create']:
                needed_repos.append(bundle_repo['project'])

    # Add any repos from lines with 'yaml::'
    match_string = 'yaml::'
    config_file = open(config, 'r')
    for line in config_file:
        if match_string in line:
            # Extract repo name
            needed_repos.append(line.partition(match_string)[2].split('/')[1])
    # Remove duplicates
    needed_repos = list(set(needed_repos))

    # Clone only the needed repos
    repo_dict = experiment_dict['build jedi']['bundle repos']
    for d in repo_dict:
        if d['project'] in needed_repos:
            project = d['project']
            git_url = d['git url']
            branch = d['branch']
            proj_dir = os.path.join(experiment_dict['bundle_dir'], project)
            git_got(git_url, branch, proj_dir, logger)

    # Expand yaml
    # -----------
    recursive_yaml_expansion(experiment_dict)

    # Resolve all dictionary definitions for full yaml
    # ------------------------------------------------
    experiment_dict = resolve_definitions(experiment_dict)

    # Prepare the suite driver file
    # -----------------------------
    prepare_suite(logger, experiment_dict)

    # Write the complete experiment yaml to suite directory
    # -----------------------------------------------------
    output_file_name = os.path.join(experiment_dict['suite_dir'], 'experiment-filled.yaml')
    with open(output_file_name, 'w') as output_file:
        yaml.dump(experiment_dict, output_file, default_flow_style=False)

    # Write out launch command for convenience
    # ----------------------------------------
    logger.info(' ')
    logger.info('  Experiment successfully installed. To launch experiment use: ')
    logger.info('  swell_launch_experiment --suite_path ' + experiment_dict['suite_dir'])
    logger.info(' ')


# --------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    main()


# --------------------------------------------------------------------------------------------------
