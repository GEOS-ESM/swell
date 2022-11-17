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

from swell.swell_path import get_swell_path
from swell.utilities.jinja2 import template_string_jinja2


# --------------------------------------------------------------------------------------------------

def copy_eva_files(logger, swell_suite_path, exp_suite_path, model_components):

    # Copy suite related files to the suite directory
    # -----------------------------------------------
    for model_component in model_components:
        src_eva_file = f'eva.yaml'
        dst_eva_file = f'eva-{model_component}.yaml'
        src_path_file = os.path.join(swell_suite_path, model_component, src_eva_file)
        dst_path_file = os.path.join(exp_suite_path, dst_eva_file)
        if os.path.exists(src_path_file):
            logger.trace(f'Copying {src_path_file} to {dst_path_file}')
            shutil.copy(src_path_file, dst_path_file)


# --------------------------------------------------------------------------------------------------

def copy_platform_files(logger, exp_suite_path, platform=None):

    # Copy platform related files to the suite directory
    # --------------------------------------------------
    if platform is not None:
        plat_mod = importlib.import_module('swell.deployment.platforms.'+platform+'.install_path')
        return_platform_install_path_call = getattr(plat_mod, 'return_platform_install_path')
        platform_path = return_platform_install_path_call()

        for s in ['modules', 'r2d2_config.yaml']:
            src_file = os.path.split(s)[1]
            src_path_file = os.path.join(platform_path, os.path.split(s)[0], src_file)
            dst_path_file = os.path.join(exp_suite_path, '{}'.format(src_file))
            if os.path.exists(src_path_file):
                logger.trace('Copying {} to {}'.format(src_path_file, dst_path_file))
                shutil.copy(src_path_file, dst_path_file)


# --------------------------------------------------------------------------------------------------


def set_swell_path_in_modules(logger, exp_suite_path):

    # Modules file
    # ------------
    modules_file = os.path.join(exp_suite_path, 'modules')

    # Only do if the suite needs modules
    # ----------------------------------
    if os.path.exists(modules_file):

        # Swell bin path
        # --------------
        swell_bin_path = shutil.which("swell_task")
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
        swell_paths = {}
        swell_paths['swell_bin_path'] = swell_bin_path
        swell_paths['swell_lib_path'] = swell_lib_path
        swell_paths['swell_sui_path'] = swell_sui_path

        # Open the file
        # -------------
        with open(modules_file, 'r') as modules_file_open:
            modules_file_str = modules_file_open.read()

        # Resolve templates
        # -----------------
        modules_file_str = template_string_jinja2(logger, modules_file_str, swell_paths)

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
