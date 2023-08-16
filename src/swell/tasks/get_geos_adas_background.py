# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import datetime
import glob
import os
import re

from swell.tasks.base.task_base import taskBase


# --------------------------------------------------------------------------------------------------


class GetGeosAdasBackground(taskBase):

    def execute(self):

        # Get the path and pattern for the background files
        # -------------------------------------------------
        background_path = self.config.path_to_geos_adas_background()

        # Get list of ncdiags to test with
        # --------------------------------
        background_path_files = glob.glob(background_path)

        # Assert that some files were found
        # ---------------------------------
        self.logger.assert_abort(len(background_path_files) != 0, f'No background ' +
                                 f'files found in the source directory ' +
                                 f'\'{background_path}\'')

        # Loop over all the files
        # -----------------------
        for background_path_file in background_path_files:

            # Get filename from full path
            background_file = os.path.basename(background_path_file)

            # Extract the datetime part from the string
            datetime_part = re.search(r"\d{8}_\d{4}\w", background_file).group()

            # Get datetime for the file from the filename
            background_file_datetime = datetime.datetime.strptime(datetime_part, '%Y%m%d_%H%Mz')

            # Create target filename using the datetime format
            background_file_target = background_file_datetime.strftime('bkg.%Y%m%dT%H%M%SZ.nc4')

            # Target path and filename
            background_path_file_target = os.path.join(self.cycle_dir(), background_file_target)

            # Remove target file if it exists (might be a link)
            if os.path.exists(background_path_file_target):
                os.remove(background_path_file_target)

            # Create symlink from target to source
            self.logger.info(f'Creating sym link from {background_path_file} to '
                             f'{background_path_file_target}')
            os.symlink(background_path_file, background_path_file_target)


# --------------------------------------------------------------------------------------------------
