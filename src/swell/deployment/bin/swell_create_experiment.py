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
from swell.utilities.git_utils import git_got
from swell.utilities.string_utils import replace_vars
from swell.utilities.dictionary_utilities import resolve_definitions, dict_get
from swell.deployment.prep_exp_dirs import copy_suite_and_platform_files, \
                                           set_swell_path_in_modules, create_modules_csh
from swell.deployment.yaml_exploder import recursive_yaml_expansion
from swell.deployment.prep_suite import prepare_suite


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


    return



#    # Set experiment directory
#    # ------------------------
#
#    # Create experiment directory with user specified experiment ID and location, user can keep
#    # ${USER} in experiment.yaml
#    user = os.environ['USER']
#    user_template = '${USER}'
#
#    # replace all instances of ${USER}
#    for key, value in experiment_dict.items():
#        if isinstance(value, str) and user_template in value:
#            experiment_dict[key] = experiment_dict[key].replace(user_template, user)
#
#    exp_root = experiment_dict['experiment_root']
#    exp_id = experiment_dict['experiment_id']
#    experiment_dir = os.path.join(exp_root, exp_id)
#
#    # Add to dictionary
#    experiment_dict.update({'experiment_dir': experiment_dir})
#    experiment_dict.update({'USERNAME': user})
#
#    # Create the experiment directory
#    # -------------------------------
#    logger.info('Creating experiment directory: '+experiment_dir)
#    if not os.path.exists(experiment_dir):
#        os.makedirs(experiment_dir, 0o755)
#    else:
#        logger.info('Experiment directory is already present, overwriting files')
#
#    # Copy experiment.yaml to the experiment directory with the experiment id name
#    # ----------------------------------------------------------------------------
#    shutil.copy(config, os.path.join(experiment_dir, 'experiment_{}.yaml'.format(exp_id)))
#    logger.info('Experiment yaml copied to working directory...')
#
#    # Create directories within experiment directory and add key to dictionary
#    # ------------------------------------------------------------------------
#    add_dir_to_conf_mkdir(logger, experiment_dict, 'bundle_dir', 'bundle')
#    add_dir_to_conf_mkdir(logger, experiment_dict, 'jedi_build_dir', 'bundle/build', False)
#    add_dir_to_conf_mkdir(logger, experiment_dict, 'stage_dir', 'stage')
#    add_dir_to_conf_mkdir(logger, experiment_dict, 'suite_dir', exp_id+'-suite')
#    add_dir_to_conf_mkdir(logger, experiment_dict, 'cycle_dir', 'run/{{current_cycle}}', False)
#    add_dir_to_conf_mkdir(logger, experiment_dict, 'geos_dir', 'geos')
#
#    # Put the swell install path in to the config
#    # -------------------------------------------
#    swell_dir = get_swell_path()
#    add_dir_to_conf_mkdir(logger, experiment_dict, 'swell_dir', swell_dir, False)
#
#    # Resolve all dictionary definitions
#    # ----------------------------------
#    experiment_dict = resolve_definitions(experiment_dict)
#
#    # Copy files to the suite directory
#    # ---------------------------------
#    copy_suite_files(logger, experiment_dict)
#
#    # Set the swell paths in the modules file
#    # ---------------------------------------
#    set_swell_path_in_modules(logger, experiment_dict)
#
#    # Clone the git repos needed for the yaml file explosion
#    # ------------------------------------------------------
#    # User chosen clones
#    if 'build jedi' in experiment_dict:
#        if 'bundle repos' in experiment_dict['build jedi']:
#            needed_repos = []
#            bundle_repos = experiment_dict['build jedi']['bundle repos']
#            for bundle_repo in bundle_repos:
#                if 'clone on create' in bundle_repo.keys():
#                    if bundle_repo['clone on create']:
#                        needed_repos.append(bundle_repo['project'])
#
#            # Remove duplicates
#            needed_repos = list(set(needed_repos))
#
#            # Clone only the needed repos
#            repo_dict = experiment_dict['build jedi']['bundle repos']
#            for d in repo_dict:
#                if d['project'] in needed_repos:
#                    project = d['project']
#                    git_url = d['git url']
#                    branch = d['branch']
#                    proj_dir = os.path.join(experiment_dict['bundle_dir'], project)
#                    git_got(git_url, branch, proj_dir, logger)
#
#    # Expand yaml
#    # -----------
#    recursive_yaml_expansion(experiment_dict)
#
#    # Resolve all dictionary definitions for full yaml
#    # ------------------------------------------------
#    experiment_dict = resolve_definitions(experiment_dict)
#
#    # Prepare the suite driver file
#    # -----------------------------
#    prepare_suite(logger, experiment_dict)
#
#    # Write the complete experiment yaml to suite directory
#    # -----------------------------------------------------
#    output_file_name = os.path.join(experiment_dict['suite_dir'], 'experiment-filled.yaml')
#    with open(output_file_name, 'w') as output_file:
#        yaml.dump(experiment_dict, output_file, default_flow_style=False)
#
#    # Create full path to the r2d2 config file
#    # ----------------------------------------
#    r2d2_conf_path = os.path.join(experiment_dict['suite_dir'], 'r2d2_config.yaml')
#
#    # Write R2D2_CONFIG to modules
#    # ----------------------------
#    with open(os.path.join(experiment_dict['suite_dir'], 'modules'), 'a') as module_file:
#        module_file.write('export R2D2_CONFIG={}'.format(r2d2_conf_path))
#
#    # Open the r2d2 file to dictionary
#    # ------------------------------------
#    with open(r2d2_conf_path, 'r') as r2d2_file_open:
#        r2d2_file_str = r2d2_file_open.read()
#        r2d2_file_str = replace_vars(r2d2_file_str, **experiment_dict)
#
#    with open(r2d2_conf_path, 'w') as r2d2_file_open:
#        r2d2_file_open.write(r2d2_file_str)
#
#    # Create csh modules file for csh users to use when debugging
#    # -----------------------------------------------------------
#    create_modules_csh(logger, experiment_dict)
#
#    # Write out launch command for convenience
#    # ----------------------------------------
#    logger.info(' ')
#    logger.info('  Experiment successfully installed. To launch experiment use: ')
#    logger.info('  swell_launch_experiment --suite_path ' + experiment_dict['suite_dir'])
#    logger.info(' ')


# --------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    main()


# --------------------------------------------------------------------------------------------------
