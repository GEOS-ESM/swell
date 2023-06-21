# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
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


class GetGeosAdasBackground(taskBase):

    def execute(self):

        # Get the build method
        # --------------------
        background_path = self.config.path_to_geos_adas_background()

        # Get list of ncdiags to test with
        # --------------------------------
        search_pattern = '*traj*.nc*'
        background_path_files_pattern = os.path.join(background_path, search_pattern)
        background_path_files = glob.glob(background_path_files_pattern)

        # Filename format
        source_filename_format = "%Y-%m-%d"
        target_filename_format = 'bkg.%Y%m%dT%H%M%SZ.nc4'

        # Assert that some files were found
        self.logger.assert_abort(len(background_path_files) != 0 is not None, f'No background ' +
                                 f'files found in the source directory ' +
                                 f'\'{background_path}/{search_pattern}\'')

        # Loop over all the files
        # -----------------------
        for background_path_file in background_path_files:

            # Get filename from full path
            background_file = os.path.basename(background_path_file)

            # Get datetime for the file from the filename
            background_file_datetime = datetime.strptime(background_file, filename_format)

            # Create target filename using the datetime format
            background_file_target = background_file_datetime.strftime(target_filename_format)

            # Target path and filename
            background_path_file_target = os.path.join(self.cycle_dir(), background_file_target)

            # Remove target file if it exists (might be a link)
            if os.path.exists(background_file_target):
                os.remove(background_file_target)

            # Create symlink from target to source
            self.logger.info(f'Creating sym link from {background_path_file} to '
                             f'{background_path_file_target}')
            os.symlink(background_path_file, background_path_file_target)


# --------------------------------------------------------------------------------------------------
