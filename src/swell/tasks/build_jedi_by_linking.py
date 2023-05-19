# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from jedi_bundle.bin.jedi_bundle import execute_tasks

from swell.tasks.base.task_base import taskBase
from swell.utilities.build import build_and_source_dirs, link_path


# --------------------------------------------------------------------------------------------------


class BuildJediByLinking(taskBase):

    def execute(self):

        # Get the build method
        # --------------------
        jedi_build_method = self.config_get('jedi_build_method')

        # Get the experiment/jedi_bundle directory
        # ----------------------------------------
        swell_exp_path = self.experiment_path()
        jedi_bundle_path = os.path.join(swell_exp_path, 'jedi_bundle')

        # Get paths to build and source
        # -----------------------------
        jedi_bundle_build_path, jedi_bundle_source_path = build_and_source_dirs(jedi_bundle_path)

        # Choice to link to existing build or build JEDI using jedi_bundle
        # ----------------------------------------------------------------
        if jedi_build_method == 'use_existing':

            # Get the existing build directory from the dictionary
            existing_build_directory = self.config_get('existing_build_directory')

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

            # Link the source code directory
            link_path(existing_build_directory, jedi_bundle_build_path)

        else:

            self.logger.abort(f'Found \'{jedi_build_method}\' for jedi_build_method in the '
                              f'experiment dictionary. Must be \'use_existing\'.')


# --------------------------------------------------------------------------------------------------
