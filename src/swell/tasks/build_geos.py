# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from swell.tasks.base.task_base import taskBase
from swell.utilities.build import build_and_source_dirs
from swell.utilities.shell_commands import run_subprocess, create_executable_file


# --------------------------------------------------------------------------------------------------


class BuildGeos(taskBase):

    def execute(self):

        # Get the build method
        # --------------------
        geos_build_method = self.config_get('geos_build_method')

        # Get the experiment/geos directory
        # ---------------------------------
        swell_exp_path = self.get_swell_exp_path()
        geos_gcm_path = os.path.join(swell_exp_path, 'GEOSgcm')

        # Get paths to build and source
        # -----------------------------
        geos_gcm_build_path, geos_gcm_source_path = build_and_source_dirs(geos_gcm_path)
        os.makedirs(geos_gcm_build_path, exist_ok=True)

        # Check that the choice is to create build
        # ----------------------------------------
        if not geos_build_method == 'create':
            self.logger.abort(f'Found \'{jedi_build_method}\' for jedi_build_method in the '
                                          f'experiment dictionary. Must be \'create\'.')

        # Create script that encapsulates the steps of building GEOS
        # ----------------------------------------------------------
        make_file_name = os.path.join(geos_gcm_build_path, 'build_geos.sh')

        # Modules file
        modules_file = os.path.join(geos_gcm_source_path, '@env', 'g5_modules.sh')

        # Install location
        geos_gcm_install_path = os.path.join(geos_gcm_path, 'install')

        make_file = f'#!/bin/bash \n' + \
                    f'cd {geos_gcm_build_path} \n' + \
                    f'source {modules_file} \n' + \
                    f'module list \n' + \
                    f'cmake -DBASEDIR=$BASEDIR/Linux -DCMAKE_Fortran_COMPILER=ifort ' + \
                    f'-DCMAKE_INSTALL_PREFIX={geos_gcm_install_path} {geos_gcm_source_path} \n' + \
                    f'make -j24 install'

        create_executable_file(self.logger, make_file_name, make_file)

        # Containerized run of the GEOS build steps
        # -----------------------------------------
        self.logger.info(f'Running GEOS build by executing {make_file_name}')
        run_subprocess(self.logger, make_file_name)


# --------------------------------------------------------------------------------------------------
