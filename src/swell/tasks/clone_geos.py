# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import tarfile
import urllib.request

from swell.tasks.base.task_base import taskBase
from swell.utilities.build import build_and_source_dirs, link_path
from swell.utilities.git_utils import git_clone
from swell.utilities.shell_commands import run_subprocess

# --------------------------------------------------------------------------------------------------


class CloneGeos(taskBase):

    def execute(self):

        # Get the build method
        # --------------------
        geos_build_method = self.config_get('geos_build_method')

        # Get the experiment/geos directory
        # ---------------------------------
        swell_exp_path = self.experiment_path()
        geos_gcm_path = os.path.join(swell_exp_path, 'GEOSgcm')

        # Get paths to build and source
        # -----------------------------
        geos_gcm_build_path, geos_gcm_source_path = build_and_source_dirs(geos_gcm_path)

        # Choice to link to existing build or build GEOS
        # ----------------------------------------------
        if geos_build_method == 'use_existing':

            # Get the existing bundle directory to get the source code
            existing_geos_gcm_source_path = self.config_get('existing_geos_gcm_source_path')

            # Link the source code directory
            link_path(existing_geos_gcm_source_path, geos_gcm_source_path)

        elif geos_build_method == 'create':

            # Get tag to build
            geos_gcm_tag = self.config_get('geos_gcm_tag')

            # Make sure tag is prepended with 'v'
            if geos_gcm_tag[0] != 'v':
                geos_gcm_tag = 'v' + geos_gcm_tag

            # Clone repo
            git_url = 'https://github.com/GEOS-ESM/GEOSgcm'
            source_dir = os.path.join(geos_gcm_path, 'source')
            git_clone(self.logger, git_url, geos_gcm_tag, source_dir, change_branch=True)

            # Use mepo to recursively clone the other needed repos
            cwd = os.getcwd()
            os.chdir(source_dir)
            self.logger.info('Cloning GEOS repos using mepo')
            run_subprocess(self.logger, ['mepo', 'clone'])
            os.chdir(cwd)

        else:

            self.logger.abort(f'Found \'{geos_build_method}\' for geos_build_method in the '
                              f'experiment dictionary. Must be \'use_existing\' or \'create\'.')


# --------------------------------------------------------------------------------------------------
