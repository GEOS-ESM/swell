# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import copy
import datetime
import os
import shutil
import sys
import yaml

from swell.deployment.prepare_config_and_suite.prepare_config_and_suite import \
     PrepareExperimentConfigAndSuite
from swell.swell_path import get_swell_path
from swell.utilities.dictionary import add_comments_to_dictionary, dict_get
from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.logger import Logger
from swell.utilities.slurm import prepare_scheduling_dict


# --------------------------------------------------------------------------------------------------


def clone_config(configuration, experiment_id, method, platform, advanced):

    # Create a logger
    logger = Logger('SwellCloneExperiment')

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


def prepare_config(suite, method, platform, override, advanced, slurm):

    # Create a logger
    # ---------------
    logger = Logger('SwellPrepSuiteConfig')

    # Assert valid method
    # -------------------
    valid_tasks = ['defaults', 'cli']
    if method not in valid_tasks:
        logger.abort(f'In Suites constructor method \'{method}\' not one of the valid ' +
                     f'tasks {valid_tasks}')

    # Set the object that will be used to populate dictionary options
    # ---------------------------------------------------------------
    prepare_config_and_suite = PrepareExperimentConfigAndSuite(logger, suite, platform,
                                                               method, override)

    # Ask questions as the suite gets configured
    # ------------------------------------------
    experiment_dict, comment_dict = prepare_config_and_suite.ask_questions_and_configure_suite()
    # Add the datetime to the dictionary
    # ----------------------------------
    experiment_dict['datetime_created'] = datetime.datetime.today().strftime("%Y%m%d_%H%M%SZ")
    comment_dict['datetime_created'] = 'Datetime this file was created (auto added)'

    # Add the platform the dictionary
    # -------------------------------
    experiment_dict['platform'] = platform
    comment_dict['platform'] = 'Computing platform to run the experiment'

    # Add the suite_to_run to the dictionary
    # --------------------------------------
    experiment_dict['suite_to_run'] = suite
    comment_dict['suite_to_run'] = 'Record of the suite being executed'

    # Add the model components to the dictionary
    # ------------------------------------------
    if 'models' in experiment_dict:
        experiment_dict['model_components'] = list(experiment_dict['models'].keys())
        comment_dict['model_components'] = 'List of models in this experiment'

    # Expand experiment dict with SLURM overrides.
    # NOTE: This is a bit of a hack. We should really either commit to using a
    # separate file and pass it around everywhere, or commit fully to keeping
    # everything in `experiment.yaml` and support it through the Questionary
    # infrastructure.
    # ----------------------------------
    if slurm is not None:
        logger.info(f"Reading SLURM directives from {slurm}.")
        assert os.path.exists(slurm)
        with open(slurm, "r") as slurmfile:
            slurm_dict = yaml.safe_load(slurmfile)
        # Ensure that SLURM dict is _only_ used for SLURM directives.
        slurm_invalid_keys = set(slurm_dict.keys()).difference({
            "slurm_directives_global",
            "slurm_directives_tasks"
        })
        if slurm_invalid_keys:
            logger.abort(f'SLURM file contains invalid keys: {slurm_invalid_keys}')
        experiment_dict = {**experiment_dict, **slurm_dict}

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
    return experiment_dict_string_comments


# --------------------------------------------------------------------------------------------------


def create_experiment_directory(suite, method, platform, override, advanced, slurm):

    # Create a logger
    # ---------------
    logger = Logger('SwellCreateExperiment')

    # Call the experiment config and suite generation
    # ------------------------------------------------
    experiment_dict_str = prepare_config(suite, method, platform, override, advanced, slurm)

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

    # At this point we need to write the complete suite file with all templates resolved. Call the
    # function to build the scheduling dictionary, combine with the experiment dictionary,
    # resolve the templates and write the suite file to the experiment suite directory.
    # --------------------------------------------------------------------------------------------
    swell_suite_path = os.path.join(get_swell_path(), 'suites', suite)
    prepare_cylc_suite_jinja2(logger, swell_suite_path, exp_suite_path, experiment_dict, platform)

    # Copy suite and platform files to experiment suite directory
    # -----------------------------------------------------------
    swell_suite_path = os.path.join(get_swell_path(), 'suites', suite)
    copy_platform_files(logger, exp_suite_path, platform)

    if os.path.exists(os.path.join(swell_suite_path, 'eva')):
        copy_eva_files(logger, swell_suite_path, exp_suite_path)

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
    logger.info(' ', False)
    logger.info('  swell launch ' + exp_suite_path, False)
    logger.info(' ', False)


# --------------------------------------------------------------------------------------------------


def copy_eva_files(logger, swell_suite_path, exp_suite_path):

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


def copy_platform_files(logger, exp_suite_path, platform=None):

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
                logger.trace('Copying {} to {}'.format(src_path_file, dst_path_file))
                shutil.copy(src_path_file, dst_path_file)


# --------------------------------------------------------------------------------------------------


def template_modules_file(logger, experiment_dict, exp_suite_path):

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


def create_modules_csh(logger, exp_suite_path):

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


def prepare_cylc_suite_jinja2(logger, swell_suite_path, exp_suite_path, experiment_dict, platform):

    # Open suite file from swell
    # --------------------------
    with open(os.path.join(swell_suite_path, 'flow.cylc'), 'r') as file:
        suite_file = file.read()

    # Copy the experiment dictionary to the rendering dictionary
    # ----------------------------------------------------------
    render_dictionary = copy.deepcopy(experiment_dict)

    # Get unique list of cycle times with model flags to render dictionary
    # --------------------------------------------------------------------

    # Convenience - fetch model_components prior to search for 'cycle_times' and 'ensemble_*'
    model_components = dict_get(logger, experiment_dict, 'model_components', [])

    # Check if 'cycle_times' appears anywhere in the suite_file
    if 'cycle_times' in suite_file:

        # Since cycle times are used, the render_dictionary will need to include cycle_times
        # If there are different model components then process each to gather cycle times
        if len(model_components) > 0:
            cycle_times = []
            for model_component in model_components:
                cycle_times_mc = experiment_dict['models'][model_component]['cycle_times']
                cycle_times = list(set(cycle_times + cycle_times_mc))
            cycle_times.sort()

            cycle_times_dict_list = []
            for cycle_time in cycle_times:
                cycle_time_dict = {}
                cycle_time_dict['cycle_time'] = cycle_time
                for model_component in model_components:
                    cycle_time_dict[model_component] = False
                    if cycle_time in experiment_dict['models'][model_component]['cycle_times']:
                        cycle_time_dict[model_component] = True
                cycle_times_dict_list.append(cycle_time_dict)

            render_dictionary['cycle_times'] = cycle_times_dict_list

        # Otherwise check that experiment_dict has cycle_times
        elif 'cycle_times' in experiment_dict:

            cycle_times = list(set(experiment_dict['cycle_times']))
            cycle_times.sort()
            render_dictionary['cycle_times'] = cycle_times

        else:

            # Otherwise use logger to abort
            logger.abort('The suite file required cycle_times but there are no model components ' +
                         'to gather them from or they are not provided in the experiment ' +
                         'dictionary.')

    # Check if 'ensemble_hofx_strategy' appears anywhere in suite_file
    ensemble_list = ['ensemble_'+s for s in ['num_members', 'hofx_strategy', 'hofx_packets']]
    ensemble_list = ensemble_list + ['skip_ensemble_hofx']
    for ensemble_aspect in ensemble_list:
        if ensemble_aspect in suite_file:
            if len(model_components) == 0:
                logger.abort(f'The suite file required {ensemble_aspect} ' +
                             'there are no model components to gather them from or ' +
                             'they are not provided in the experiment dictionary.')
            for model_component in model_components:
                render_dictionary[ensemble_aspect] = \
                    experiment_dict['models'][model_component][ensemble_aspect]

    # Cycling VarBC exception (only for geos_atmosphere)
    if 'cycling_varbc' in suite_file:
        if 'geos_atmosphere' in model_components:
            render_dictionary['cycling_varbc'] = \
                experiment_dict['models']['geos_atmosphere']['cycling_varbc']
        else:
            logger.abort('The suite file required cycling_varbc but ' +
                         'geos_atmosphere is not in the model components.')

    # Marine model toggles (only for geos_marine)
    if 'marine_models' in suite_file:
        if 'geos_marine' in model_components:
            render_dictionary['marine_models'] = \
                experiment_dict['models']['geos_marine']['marine_models']
        else:
            logger.abort('The suite file required marine_models but ' +
                         'geos_marine is not in the model components.')

    render_dictionary['scheduling'] = prepare_scheduling_dict(logger, experiment_dict, platform)

    # Default execution time limit for everthing is PT1H
    for slurm_task in render_dictionary['scheduling'].keys():
        render_dictionary['scheduling'][slurm_task]['execution_time_limit'] = 'PT1H'

    # Set some specific values for:
    # ------------------------------
    # run time (note: these overwrite defaults above)
    render_dictionary['scheduling']['BuildJedi']['execution_time_limit'] = 'PT3H'
    render_dictionary['scheduling']['EvaObservations']['execution_time_limit'] = 'PT30M'

    # Render the template
    # -------------------
    new_suite_file = template_string_jinja2(logger, suite_file, render_dictionary, False)

    # Write suite file to experiment
    # ------------------------------
    with open(os.path.join(exp_suite_path, 'flow.cylc'), 'w') as file:
        file.write(new_suite_file)


# --------------------------------------------------------------------------------------------------
