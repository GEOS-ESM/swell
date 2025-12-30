# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import copy
import os
import shutil
import sys
import yaml
from typing import Union, Optional

from swell.deployment.prepare_config_and_suite.prepare_config_and_suite import \
     PrepareExperimentConfigAndSuite
from swell.swell_path import get_swell_path
from swell.utilities.dictionary import add_comments_to_dictionary, dict_get, update_dict
from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.logger import Logger, get_logger
from swell.utilities.slurm import prepare_slurm_defaults_and_overrides
from swell.suites.base.all_suites import suite_configs, workflows
from swell.utilities.check_da_params import check_da_params


# --------------------------------------------------------------------------------------------------


def clone_config(
    configuration: str,
    experiment_id: str,
    method: str,
    platform: str,
    advanced: bool
) -> str:

    # Create a logger
    logger = get_logger('SwellCloneExperiment')

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


def prepare_config(
    suite: str,
    suite_config: str,
    method: str,
    platform: str,
    override: Union[dict, str, None],
    advanced: bool,
    slurm: str
) -> str:

    # Create a logger
    # ---------------
    logger = get_logger('SwellPrepSuiteConfig')

    # Assert valid method
    # -------------------
    valid_tasks = ['defaults', 'cli']
    if method not in valid_tasks:
        logger.abort(f'In Suites constructor method \'{method}\' not one of the valid ' +
                     f'tasks {valid_tasks}')

    # Set the object that will be used to populate dictionary options
    # ---------------------------------------------------------------
    prepare_config_and_suite = PrepareExperimentConfigAndSuite(logger, suite, suite_config,
                                                               platform, method, override)

    # Retrieved the answered suite questions
    # --------------------------------------
    suite_dict = prepare_config_and_suite.experiment_dict.copy()

    # Overrides for comparison suites
    if 'start_cycle_point' in suite_dict:
        start_cycle_point = suite_dict['start_cycle_point']
        final_cycle_point = suite_dict['final_cycle_point']
        if 'comparison_experiment_paths' in suite_dict and \
                suite_dict['start_cycle_point'] is None:
            config_list = suite_dict['comparison_experiment_paths']
            for model in suite_dict['model_components']:
                cycle_times = suite_dict['models'][model]['cycle_times']
                start_cycle_point, final_cycle_point, cycle_times = check_da_params(
                        config_list,
                        model,
                        start_cycle_point,
                        final_cycle_point,
                        cycle_times)

                suite_dict['start_cycle_point'] = start_cycle_point
                suite_dict['final_cycle_point'] = final_cycle_point
                suite_dict['models'][model]['cycle_times'] = cycle_times

    # Resolve cycle times for models
    # ------------------------------
    if 'models' in suite_dict and 'start_cycle_point' in suite_dict:
        model_components = suite_dict['models']

        # Since cycle times are used, the render_dictionary will need to include cycle_times
        # If there are different model components then process each to gather cycle times
        if len(model_components) > 0 and all('cycle_times' in suite_dict['models'][model]
                                             for model in model_components):
            cycle_times = []
            for model_component in model_components:
                cycle_times_mc = suite_dict['models'][model_component]['cycle_times']
                cycle_times = list(set(cycle_times + cycle_times_mc))
            cycle_times.sort()

            cycle_times_dict_list = []
            for cycle_time in cycle_times:
                cycle_time_dict = {}
                cycle_time_dict['cycle_time'] = cycle_time
                for model_component in model_components:
                    cycle_time_dict[model_component] = False
                    if cycle_time in suite_dict['models'][model_component]['cycle_times']:
                        cycle_time_dict[model_component] = True
                cycle_times_dict_list.append(cycle_time_dict)

            suite_dict['cycle_times'] = cycle_times_dict_list

        # Otherwise check that suite_dict has cycle_times
        elif 'cycle_times' in suite_dict:

            cycle_times = list(set(suite_dict['cycle_times']))
            cycle_times.sort()
            suite_dict['cycle_times'] = cycle_times

    # Get the slurm defaults from the user and platform
    # -------------------------------------------------
    slurm_dict = prepare_slurm_defaults_and_overrides(logger, platform, slurm)

    # Initialize the workflow
    # -----------------------
    workflow_class = workflows.get_workflow(suite)
    workflow = workflow_class(suite_dict, slurm_dict)

    # Get the list of tasks from the workflow's graph
    # -----------------------------------------------
    model_ind_tasks, model_dep_tasks = workflow.get_independent_and_model_tasks()

    # Set the tasks to be used in preparing the suite
    # -----------------------------------------------
    prepare_config_and_suite.model_independent_tasks = model_ind_tasks
    prepare_config_and_suite.model_dependent_tasks = model_dep_tasks

    # Ask the task questions
    # ----------------------
    experiment_dict, comment_dict = prepare_config_and_suite.configure_and_ask_task_questions()

    if 'start_cycle_point' in suite_dict:
        experiment_dict['start_cycle_point'] = suite_dict['start_cycle_point']
        experiment_dict['final_cycle_point'] = suite_dict['final_cycle_point']

    # Update dict with cycle times
    # ----------------------------
    workflow_dict = update_dict(experiment_dict, suite_dict)
    workflow.experiment_dict = workflow_dict

    # Finalize the workflow by adding the runtime section, and get the contents
    # -------------------------------------------------------------------------
    workflow_string = workflow.get_workflow_string()

    # Expand all environment vars in the dictionary
    # ---------------------------------------------
    experiment_dict_string = yaml.dump(experiment_dict, default_flow_style=False, sort_keys=False)
    experiment_dict_string = os.path.expandvars(experiment_dict_string)
    experiment_dict = yaml.safe_load(experiment_dict_string)

    # Add comments to dictionary
    # --------------------------
    experiment_dict_string = yaml.dump(experiment_dict, default_flow_style=False, sort_keys=False)

    experiment_dict_string_comments = add_comments_to_dictionary(logger, experiment_dict_string,
                                                                 comment_dict)

    # Return path to dictionary file
    # ------------------------------

    return experiment_dict_string_comments, workflow_string


# --------------------------------------------------------------------------------------------------


def create_experiment_directory(
    suite_config: str,
    method: str,
    platform: str,
    override: str,
    advanced: bool,
    slurm: Optional[str]
) -> None:

    # Get the base name of the suite
    # ------------------------------
    suite = suite_configs.base_suite(suite_config)

    # Create a logger
    # ---------------
    logger = get_logger('SwellCreateExperiment')

    # Call the experiment config and suite generation
    # ------------------------------------------------
    experiment_dict_str, workflow_str = prepare_config(suite, suite_config, method, platform,
                                                       override, advanced, slurm)

    # Load the string using yaml
    # --------------------------
    experiment_dict = yaml.safe_load(experiment_dict_str)

    # Experiment ID and root from the user input
    # ------------------------------------------
    experiment_id = dict_get(logger, experiment_dict, 'experiment_id')
    experiment_root = dict_get(logger, experiment_dict, 'experiment_root')

    # Write out some info
    # -------------------
    logger.info(f'Creating experiment: \'{experiment_id}\' in \'{experiment_root}\'')

    # Make the suite directory
    # ------------------------
    exp_path = os.path.join(experiment_root, experiment_id)
    exp_suite_path = os.path.join(exp_path, experiment_id+'-suite')

    os.makedirs(exp_suite_path, 0o755, exist_ok=True)

    # Write dictionary (with comments) to YAML file
    # ---------------------------------------------
    with open(os.path.join(exp_suite_path, 'experiment.yaml'), 'w') as file:
        file.write(experiment_dict_str)

    with open(os.path.join(exp_suite_path, 'flow.cylc'), 'w') as file:
        file.write(workflow_str)

    # Copy suite and platform files to experiment suite directory
    # -----------------------------------------------------------
    swell_suite_path = os.path.join(get_swell_path(), 'suites', suite)
    copy_platform_files(logger, exp_suite_path, platform)

    if os.path.exists(os.path.join(swell_suite_path, 'eva')):
        copy_eva_files(swell_suite_path, exp_suite_path)

    # Set the swell paths in the modules file and create csh versions
    # ---------------------------------------------------------------
    template_modules_file(logger, experiment_dict, exp_suite_path)
    create_modules_csh(logger, exp_suite_path)

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
    logger.info('Experiment successfully installed. To launch experiment use: ')
    logger.info(' ')
    logger.info('  swell launch ' + exp_suite_path)
    logger.info(' ')


# --------------------------------------------------------------------------------------------------


def copy_eva_files(
    swell_suite_path: str,
    exp_suite_path: str
) -> None:

    # Repo eva files
    eva_directory = os.path.join(swell_suite_path, 'eva')

    # Destination for eva files
    destination_directory = os.path.join(exp_suite_path, 'eva')

    # If destination directory exists, delete it
    if os.path.exists(destination_directory):
        shutil.rmtree(destination_directory)

    # Copy all the files
    shutil.copytree(eva_directory, destination_directory)


# --------------------------------------------------------------------------------------------------


def copy_platform_files(
    logger: Logger,
    exp_suite_path: str,
    platform: Optional[str] = None
) -> None:

    # Copy platform related files to the suite directory
    # --------------------------------------------------
    if platform is not None:
        swell_lib_path = get_swell_path()
        platform_path = os.path.join(swell_lib_path, 'deployment', 'platforms', platform)

        for s in ['modules']:
            src_file = os.path.split(s)[1]
            src_path_file = os.path.join(platform_path, os.path.split(s)[0], src_file)
            dst_path_file = os.path.join(exp_suite_path, '{}'.format(src_file))
            if os.path.exists(src_path_file):
                logger.debug('Copying {} to {}'.format(src_path_file, dst_path_file))
                shutil.copy(src_path_file, dst_path_file)


# --------------------------------------------------------------------------------------------------


def template_modules_file(
    logger: Logger,
    experiment_dict: dict,
    exp_suite_path: str
) -> None:

    # Modules file
    # ------------
    modules_file = os.path.join(exp_suite_path, 'modules')

    # Only do if the suite needs modules
    # ----------------------------------
    if os.path.exists(modules_file):

        # Swell bin path
        # --------------
        swell_bin_path = shutil.which("swell")
        swell_bin_path = os.path.split(swell_bin_path)[0]

        # Swell lib path
        # --------------
        swell_lib_path = get_swell_path()
        swell_lib_path = os.path.split(swell_lib_path)[0]

        # Swell suite path
        # ----------------
        swell_sui_path = os.path.join(get_swell_path(), 'suites')

        # Dictionary of definitions
        # -------------------------
        modules_dict = copy.copy(experiment_dict)
        modules_dict['swell_bin_path'] = swell_bin_path
        modules_dict['swell_lib_path'] = swell_lib_path
        modules_dict['swell_sui_path'] = swell_sui_path

        # Determine the python major/minor version and put in template dict
        # -----------------------------------------------------------------
        modules_dict['python_majmin'] = f'{sys.version_info.major}.{sys.version_info.minor}'

        # Open the file
        # -------------
        with open(modules_file, 'r') as modules_file_open:
            modules_file_str = modules_file_open.read()

        # Resolve templates
        # -----------------
        modules_file_str = template_string_jinja2(logger, modules_file_str, modules_dict)

        # Overwrite the file
        # ------------------
        with open(modules_file, 'w') as modules_file_open:
            modules_file_open.write(modules_file_str)

# --------------------------------------------------------------------------------------------------


def create_modules_csh(
    logger: Logger,
    exp_suite_path: str
) -> None:

    # Modules file
    # ------------
    modules_file = os.path.join(exp_suite_path, 'modules')

    # Only do if the suite needs modules
    # ----------------------------------
    if os.path.exists(modules_file):

        # Open the file
        # -------------
        with open(modules_file, 'r') as modules_file_open:
            modules_file_lines = modules_file_open.readlines()

        # Replace some things
        # -------------------
        for idx, modules_file_line in enumerate(modules_file_lines):

            # 'bash' to 'csh'
            if 'bash' in modules_file_line:
                modules_file_lines[idx] = modules_file_lines[idx].replace('bash', 'csh')

            # Export to setenv
            if 'export' in modules_file_line:
                modules_file_lines[idx] = modules_file_lines[idx].replace('export', 'setenv')
                modules_file_lines[idx] = modules_file_lines[idx].replace('=', ' ')

            # Set PYTHONPATH
            if 'PYTHONPATH=' in modules_file_line:
                modules_file_lines[idx] = modules_file_lines[idx].replace('PYTHONPATH=',
                                                                          'setenv PYTHONPATH ')

            # Set path
            if 'PATH=' in modules_file_line:
                modules_file_lines[idx] = modules_file_lines[idx].replace('PATH=', 'set path = (')
                modules_file_lines[idx] = modules_file_lines[idx].replace(':$PATH', ' $path)')

        # Overwrite the file
        # ------------------
        with open(modules_file+'-csh', 'w') as modules_file_open:
            for modules_file_line in modules_file_lines:
                modules_file_open.write(modules_file_line)


# --------------------------------------------------------------------------------------------------
