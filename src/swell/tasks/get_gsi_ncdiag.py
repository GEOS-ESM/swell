# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import glob
import os

from swell.tasks.base.task_base import taskBase


# --------------------------------------------------------------------------------------------------


class GetGsiNcdiag(taskBase):

    def execute(self) -> None:

        # Get the build method
        # --------------------
        gsi_diag_path = self.config.path_to_gsi_nc_diags()

        # Replace gsi_diag_path datetime string with the actual datetime
        # --------------------------------------------------------------
        cycle_time_dto = self.cycle_time_dto()
        gsi_diag_path = cycle_time_dto.strftime(gsi_diag_path)

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

        # Create another directory to hold the aircraft data
        # --------------------------------------------------
        prof_files = glob.glob(os.path.join(gsi_diag_dir, '*prof*.nc4'))

        for prof_file in prof_files:
            os.makedirs(os.path.join(gsi_diag_dir, 'aircraft'), 0o755, exist_ok=True)

            # Replace _prof with nothing
            file_name = os.path.basename(prof_file)
            file_name = file_name.replace('_prof', '')

            # Move the file into the prof directory
            os.rename(prof_file, os.path.join(gsi_diag_dir, 'aircraft', file_name))


# --------------------------------------------------------------------------------------------------
