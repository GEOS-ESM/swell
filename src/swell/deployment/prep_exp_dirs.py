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

    suite_dict = experiment_dict['suite']
    suite_name = suite_dict['suite name']

    # Copy suite related files to the suite directory
    # -----------------------------------------------
    suite_path = return_suite_path()
    for s in [os.path.join(suite_name, 'jedi_config.yaml'), os.path.join(suite_name, 'flow.cylc')]:
        src_file = os.path.split(s)[1]
        src_path_file = os.path.join(suite_path, os.path.split(s)[0], src_file)
        dst_path_file = os.path.join(suite_dir, '{}'.format(src_file))
        if os.path.exists(src_path_file):
            logger.trace('Copying {} to {}'.format(src_path_file, dst_path_file))
            shutil.copy(src_path_file, dst_path_file)

    # Copy platform related files to the suite directory
    # --------------------------------------------------
    if 'platform' in suite_dict:
        platform = suite_dict['platform']
        plat_mod = importlib.import_module('swell.deployment.platforms.'+platform+'.install_path')
        return_platform_install_path_call = getattr(plat_mod, 'return_platform_install_path')
        platform_path = return_platform_install_path_call()

        for s in ['modules']:
            src_file = os.path.split(s)[1]
            src_path_file = os.path.join(platform_path, os.path.split(s)[0], src_file)
            dst_path_file = os.path.join(suite_dir, '{}'.format(src_file))
            if os.path.exists(src_path_file):
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

    # Only do if the suite needs modules
    # ----------------------------------
    if os.path.exists(modules_file):

        # Swell bin path
        # --------------
        swell_bin_path = shutil.which("swell_task")
        swell_bin_path = os.path.split(swell_bin_path)[0]

        # Swell lib path
        # --------------
        swell_lib_path = swell_install_path()
        swell_lib_path = os.path.split(swell_lib_path)[0]

        # Swell suite path
        # ----------------
        swell_sui_path = return_suite_path()

        # Dictionary of definitions
        # -------------------------
        swell_paths = {}
        swell_paths['swell_bin_path'] = swell_bin_path
        swell_paths['swell_lib_path'] = swell_lib_path
        swell_paths['swell_sui_path'] = swell_sui_path

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
