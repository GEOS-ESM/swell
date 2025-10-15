# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import glob
import os
import subprocess

from swell.tasks.base.task_base import taskBase


# --------------------------------------------------------------------------------------------------


class GetObsNotInR2d2(taskBase):

    def execute(self) -> None:

        # Get the cycle string
        # --------------------
        cycle_date = self.__datetime__.string_directory()

        # Get the path and pattern for the observation files
        # -------------------------------------------------
        existing_path = self.config.ioda_locations_not_in_r2d2()

        # Point to the model directory
        # ----------------------------
        existing_path = os.path.join(existing_path, cycle_date, self.__model__)

        # Create the list containing the files to process
        # -----------------------------------------------
        existing_path_files = []

        # Set the file patterns to search for
        # -----------------------------------
        file_patterns = ['*nc4', '*txt']

        for file_pattern in file_patterns:

            # Get the full paths of all files
            # -------------------------------
            existing_path_files.extend(glob.glob(os.path.join(existing_path, file_pattern)))

        # Assert that some files were found
        # ---------------------------------
        self.logger.assert_abort(len(existing_path_files) > 0, f'No observation '
                                 'files matching cycle in observation directory.')

        # Loop over all the files
        # -----------------------
        for existing_path_file in existing_path_files:

            # Get filename from full path
            # ---------------------------
            existing_file = os.path.basename(existing_path_file)

            # Set the target file
            # -------------------
            existing_path_file_target = os.path.join(self.cycle_dir(), existing_file)

            # Remove the file if it exists
            # ----------------------------
            if os.path.exists(existing_path_file_target):
                os.remove(existing_path_file_target)

            # Build the copy command
            # ----------------------
            command = ['ln', '-s', existing_path_file, existing_path_file_target]

            self.logger.info(f'Linking {existing_path_file} '
                             f'to {existing_path_file_target}')

            # Copy the file
            # -------------
            subprocess.run(command)

# --------------------------------------------------------------------------------------------------
