# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from swell.tasks.base.task_base import taskBase
from swell.utilities.build import build_and_source_dirs, link_path


# --------------------------------------------------------------------------------------------------


class BuildJediByLinking(taskBase):

    def execute(self):

        # Get the experiment/jedi_bundle directory
        # ----------------------------------------
        swell_exp_path = self.experiment_path()
        jedi_bundle_path = os.path.join(swell_exp_path, 'jedi_bundle')

        # Get paths to build and source
        # -----------------------------
        jedi_bundle_build_path, jedi_bundle_source_path = build_and_source_dirs(jedi_bundle_path)

        # Choice to link to existing build or build JEDI using jedi_bundle
        # ----------------------------------------------------------------
        if self.config.jedi_build_method() == 'use_existing':

            # Get the existing build directory from the dictionary
            existing_jedi_build_directory = self.config.existing_jedi_build_directory()

            # Assert that the existing build directory contains a bin directory
            if not os.path.exists(os.path.join(existing_jedi_build_directory, 'bin')):
                self.logger.abort(f'Existing JEDI build directory is provided but a bin ' +
                                  f'directory is not found in the path ' +
                                  f'\'{existing_jedi_build_directory}\'')

            # Write warning to user
            self.logger.info('Suitable JEDI build found, linking build directory. Warning: ' +
                             'problems will follow if the loaded modules are not consistent ' +
                             'with those used to build this version of JEDI. Also note that ' +
                             'this experiment may not be reproducible if the build changes.')

            # Link the source code directory
            link_path(existing_jedi_build_directory, jedi_bundle_build_path)

        else:

            self.logger.abort(f'Found \'{self.config.jedi_build_method()}\' for ' +
                              f'jedi_build_method in the experiment dictionary. Must be ' +
                              f'\'use_existing\'.')


# --------------------------------------------------------------------------------------------------
