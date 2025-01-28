# GetBufr.py
# Purpose: Find Bufr Files


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


class GetBufr(taskBase):

    def execute(self) -> None:

        # Get the build method
        # --------------------
        bufr_path = self.config.path_to_bufr()

        # Replace bufr_path datetime string with the actual datetime
        # --------------------------------------------------------------
        cycle_time_dto = self.cycle_time_dto()
        bufr_path = cycle_time_dto.strftime(bufr_path)

        # Get list of bufr to test with
        # --------------------------------
        bufr_path_files_pattern = os.path.join(bufr_path, '*bufr*')
        bufr_path_files = glob.glob(bufr_path_files_pattern)

        # Get cycle dir and create if needed
        # ----------------------------------
        bufr_dir = os.path.join(self.cycle_dir(), 'bufr')
        os.makedirs(bufr_dir, 0o755, exist_ok=True)

        # Assert that some files were found
        self.logger.assert_abort(len(bufr_path_files) != 0 is not None, f'No ncdiag ' +
                                 f'files found in the source directory ' +
                                 f'\'{bufr_path_files_pattern}\'')

        # Copy all the files into the cycle directory
        # -------------------------------------------
        for bufr_path_file in bufr_path_files:

            # Source file
            bufr_file_source = os.path.basename(bufr_path_file)

            # Target file
            bufr_file_target = os.path.join(bufr_dir, bufr_file_source)

            # Remove target file if it exists (might be a link)
            if os.path.exists(bufr_file_target):
                os.remove(bufr_file_target)

            # Create symlink from target to source
            self.logger.info(f'Creating sym link from {bufr_path_file} to '
                             f'{bufr_file_target}')
            os.symlink(bufr_path_file, bufr_file_target)
"""
        # Create another directory to hold the aircraft data
        # --------------------------------------------------
        prof_files = glob.glob(os.path.join(bufr_dir, '*prof*.nc4'))

        for prof_file in prof_files:
            os.makedirs(os.path.join(bufr_dir, 'WHAT IS THIS?: aircraft'), 0o755, exist_ok=True) # <------- still to do !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            # Replace _prof with nothing
            file_name = os.path.basename(prof_file)
            file_name = file_name.replace('_prof', '')

            # Move the file into the prof directory
            os.rename(prof_file, os.path.join(bufr_dir, 'WHAT IS THIS?: aircraft', file_name)) # <------- still to do !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

"""
# --------------------------------------------------------------------------------------------------
