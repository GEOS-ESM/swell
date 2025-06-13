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


class GetGeosJediBackground(taskBase):

    def execute(self) -> None:

        # Get the cycle string
        # --------------------
        cycle_date = self.__datetime__.string_directory()

        # Get the path and pattern for the background files
        # -------------------------------------------------
        background_path = self.config.path_to_geos_jedi_background()

        # Point to the model directory
        # ----------------------------
        background_path = os.path.join(background_path, cycle_date, self.__model__)

        # Get the full paths of all files
        # -------------------------------
        background_path_files = glob.glob(os.path.join(background_path, '*'))

        # Assert that some files were found
        # ---------------------------------
        self.logger.assert_abort(len(background_path_files) > 0, f'No background '
                                 'files matching cycle in background directory.')

        # Loop over all the files
        # -----------------------
        for background_path_file in background_path_files:
            print(background_path_file)
            # Get filename from full path
            # ---------------------------
            background_file = os.path.basename(background_path_file)

            # Set the target file
            # -------------------
            background_path_file_target = os.path.join(self.cycle_dir(), background_file)

            # Remove the file if it exists
            # ----------------------------
            if os.path.exists(background_path_file_target):
                os.remove(background_path_file_target)

            # Build the copy command
            # ----------------------
            command = ['cp', background_path_file, background_path_file_target]

            self.logger.info(f'Copying {background_path_file} '
                             f'to {background_path_file_target}', wrap=False)

            # Copy the file
            # -------------
            subprocess.run(command)

# --------------------------------------------------------------------------------------------------
