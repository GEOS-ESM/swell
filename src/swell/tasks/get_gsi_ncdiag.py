# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import glob
import os
import shutil

from swell.tasks.base.task_base import taskBase


# --------------------------------------------------------------------------------------------------


class GetGsiNcdiag(taskBase):

    def execute(self):

        # Get the build method
        # --------------------
        gsi_diag_path = self.config.path_to_gsi_nc_diags()

        # Get list of ncdiags to test with
        # --------------------------------
        gsi_diag_path_files_pattern = os.path.join(gsi_diag_path, '*ges*.nc*')
        gsi_diag_path_files = glob.glob(gsi_diag_path_files_pattern)

        # Get cycle dir and create if needed
        # ----------------------------------
        gsi_diag_dir = os.path.join(self.cycle_dir(), 'gsi_ncdiags')
        os.makedirs(gsi_diag_dir, 0o755, exist_ok=True)

        # Assert that some files were found
        self.logger.assert_abort(len(gsi_diag_path_files) != 0 is not None, f'No ncdiag ' +
                                 f'files found in the source directory ' +
                                 f'\'{gsi_diag_path_files_pattern}\'')

        # Copy all the files into the cycle directory
        # -------------------------------------------
        for gsi_diag_path_file in gsi_diag_path_files:

            # Source file
            gsi_diag_file_source = os.path.basename(gsi_diag_path_file)

            # Target file
            gsi_diag_file_target = os.path.join(gsi_diag_dir, gsi_diag_file_source)

            # Remove target file if it exists (might be a link)
            if os.path.exists(gsi_diag_file_target):
                os.remove(gsi_diag_file_target)

            # Create symlink from target to source
            self.logger.info(f'Creating sym link from {gsi_diag_path_file} to '
                             f'{gsi_diag_file_target}')
            os.symlink(gsi_diag_path_file, gsi_diag_file_target)


# --------------------------------------------------------------------------------------------------
