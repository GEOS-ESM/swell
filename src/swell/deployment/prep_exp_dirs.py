# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import importlib
import os
import pathlib
import shutil

from swell.install_path import swell_install_path
from swell.suites.suites import return_suite_path
from swell.utilities.string_utils import replace_vars


# --------------------------------------------------------------------------------------------------


def add_dir_to_conf_mkdir(logger, experiment_dict, experiment_dict_key, experiment_sub_dir,
                          make_dir=True):

    # Get experiment directory
    experiment_dir = experiment_dict['experiment_dir']
    experiment_sub_dir_full = os.path.join(experiment_dir, experiment_sub_dir)

    if make_dir:
        # Make the new directory
        os.makedirs(experiment_sub_dir_full, exist_ok=True)

        # Set permissions
        os.chmod(experiment_sub_dir_full, 0o755)

    # Add the associated key to the dictionary
    experiment_dict.update({experiment_dict_key: experiment_sub_dir_full})


# --------------------------------------------------------------------------------------------------


def copy_suite_files(logger, experiment_dict):

    # Extract config
    # --------------
    suite_dir = experiment_dict['suite_dir']
    suite_name = experiment_dict['suite']['suite name']
    platform = experiment_dict['suite']['platform']

    # Copy suite related files to the suite directory
    # -----------------------------------------------
    suite_path = return_suite_path()
    for s in [os.path.join(suite_name, 'jedi_config.yaml'), os.path.join(suite_name, 'flow.cylc')]:
        src_file = os.path.split(s)[1]
        src_path_file = os.path.join(suite_path, os.path.split(s)[0], src_file)
        dst_path_file = os.path.join(suite_dir, '{}'.format(src_file))
        logger.trace('Copying {} to {}'.format(src_path_file, dst_path_file))
        shutil.copy(src_path_file, dst_path_file)

    # Copy platform related files to the suite directory
    # --------------------------------------------------
    plat_mod = importlib.import_module('swell.deployment.platforms.'+platform+'.install_path')
    return_platform_install_path_call = getattr(plat_mod, 'return_platform_install_path')
    platform_path = return_platform_install_path_call()

    for s in ['modules']:
        src_file = os.path.split(s)[1]
        src_path_file = os.path.join(platform_path, os.path.split(s)[0], src_file)
        dst_path_file = os.path.join(suite_dir, '{}'.format(src_file))
        logger.trace('Copying {} to {}'.format(src_path_file, dst_path_file))
        shutil.copy(src_path_file, dst_path_file)


# --------------------------------------------------------------------------------------------------

def set_swell_path_in_modules(logger, experiment_dict):

    # Extract config
    # --------------
    suite_dir = experiment_dict['suite_dir']

    # Modules file
    # ------------
    modules_file = os.path.join(suite_dir, 'modules')

    # Swell bin path
    # --------------
    swell_bin_path = shutil.which("swell_task")
    swell_bin_path = "/".join(list(swell_bin_path.split('/')[0:-1]))

    # Swell lib path
    # --------------
    swell_lib_path = swell_install_path()
    swell_lib_path = "/".join(list(swell_lib_path.split('/')[0:-1]))

    # Dictionary of definitions
    # -------------------------
    swell_paths = {}
    swell_paths['swell_bin_path'] = swell_bin_path
    swell_paths['swell_lib_path'] = swell_lib_path

    # Open the file
    # -------------
    with open(modules_file, 'r') as modules_file_open:
        modules_file_str = modules_file_open.read()
        modules_file_str = replace_vars(modules_file_str, **swell_paths)

    # Overwrite the file
    # ------------------
    with open(modules_file, 'w') as modules_file_open:
        modules_file_open.write(modules_file_str)

# --------------------------------------------------------------------------------------------------

def create_modules_csh(logger, experiment_dict):

    # Extract config
    # --------------
    suite_dir = experiment_dict['suite_dir']

    # Modules file
    # ------------
    modules_file = os.path.join(suite_dir, 'modules')

    # Open the file
    # -------------
    with open(modules_file, 'r') as modules_file_open:
        modules_file_str = modules_file_open.read()

    # Replace some things
    # -------------------
    modules_file_str = modules_file_str.replace('export', 'setenv')
    modules_file_str = modules_file_str.replace('bash', 'csh')
    modules_file_str = modules_file_str.replace('=', ' ')

    modules_file_str = modules_file_str.replace('PYTHONPATH /', 'set PYTHONPATH = (/')
    modules_file_str = modules_file_str.replace('PATH /', 'set PATH = (/')
    modules_file_str = modules_file_str.replace(':$PYTHONPATH', ' $PYTHONPATH)')
    modules_file_str = modules_file_str.replace(':$PATH', ' $PATH)')

    # Overwrite the file
    # ------------------
    with open(modules_file+'-csh', 'w') as modules_file_open:
        modules_file_open.write(modules_file_str)
