# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import shutil
import subprocess

from swell.tasks.base.task_base import taskBase
from swell.utilities.git_utils import git_got


# --------------------------------------------------------------------------------------------------


class BuildJedi(taskBase):

    def execute(self):

        # Get the build method
        # --------------------
        jedi_build_method = self.config_get('jedi_build_method')

        # Get the experiment/jedi_bundle directory
        # ----------------------------------------
        swell_exp_path = self.get_swell_exp_path()
        jedi_bundle_path = os.path.join(swell_exp_path, 'jedi_bundle')
        jedi_bundle_build_path = os.path.join(jedi_bundle_path, 'build')
        jedi_bundle_source_path = os.path.join(jedi_bundle_path, 'source')

        # Make jedi_bundle directory
        # --------------------------
        os.makedirs(jedi_bundle_path, 0o755, exist_ok=True)

        # Choice to link to existing build or build JEDI using jedi_bundle
        # ----------------------------------------------------------------
        if jedi_build_method == 'use_existing':

            # Get the existing build directory from the dictionary
            existing_build_directory = self.config_get('existing_build_directory')

            # Get the existing bundle directory to get the source code
            existing_source_directory = self.config_get('existing_source_directory')

            # Assert that the existing build directory contains a bin directory
            if not os.path.exists(os.path.join(existing_build_directory, 'bin')):
                self.logger.abort(f'Existing JEDI build directory is provided but a bin ' +
                                  f'directory is not found in the path ' +
                                  f'\'{existing_build_directory}\'')

            # Write warning to user
            self.logger.info('Suitable JEDI build found, linking build directory. Warning: ' +
                             'problems will follow if the loaded modules are not consistent ' +
                             'with those used to build this version of JEDI. Also note that ' +
                             'this experiment may not be reproducible if the build changes.')

            # Remove trailing slash if needed
            if jedi_bundle_build_path.endswith('/'):
                jedi_bundle_build_path = jedi_bundle_build_path[:-1]

            if jedi_bundle_source_path.endswith('/'):
                jedi_bundle_source_path = jedi_bundle_source_path[:-1]

            # Remove existing build path if present
            if os.path.islink(jedi_bundle_build_path):  # Is a link
                os.remove(jedi_bundle_build_path)
            elif os.path.isdir(jedi_bundle_build_path):  # Is a directory
                shutil.rmtree(jedi_bundle_build_path)

            # Remove existing source path if present
            if os.path.islink(jedi_bundle_source_path):  # Is a link
                os.remove(jedi_bundle_source_path)
            elif os.path.isdir(jedi_bundle_source_path):  # Is a directory
                shutil.rmtree(jedi_bundle_source_path)

            # Link existing build into the directory
            os.symlink(existing_build_directory, jedi_bundle_build_path)

            # Link existing source into the directory
            os.symlink(existing_source_directory, jedi_bundle_source_path)

        elif jedi_build_method == 'create':

            self.logger.abort(f'Building JEDI is not yet supported')

        else:
            self.logger.abort(f'Found \'{jedi_build_method}\' for jedi_build_method in the '
                              f'experiment dictionary. Must be \'use_existing\' or \'create\'.')
