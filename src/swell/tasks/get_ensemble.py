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


class GetEnsemble(taskBase):

    def execute(self):

        # Get the path and pattern for the background files
        # -------------------------------------------------
        ensemble_path = self.config.path_to_ensemble()

        # Fetch list of ensemble members
        # --------------------------------
        ensemble_members = glob.glob(ensemble_path)

        # Assert at least one ensemble member was found
        # -----------------------------------------------
        self.logger.assert_abort(len(ensemble_members) != 0, f'No ensemble member ' +
                                 f'files found in the source directory ' +
                                 f'\'{ensemble_path}\'')

        # Loop over all the ensemble members found
        # -----------------------------------------
        for ensemble_member in ensemble_members:

            # Get filename from full path
            member_file = os.path.basename(ensemble_member)

            # Extract the datetime part from the string
            datetime_part = re.search(r"\d{8}_\d{4}\w", member_file).group()

            # Get datetime for the file from the filename
            member_file_datetime = datetime.datetime.strptime(datetime_part, '%Y%m%d_%H%Mz')

            # Create target filename using the datetime format
            member_file_target = member_file_datetime.strftime('geos.mem002.%Y%m%d_%H%M%Sz.nc4')

            # Target path and filename
            ensemble_path_file_target = os.path.join(self.cycle_dir(), member_file_target)

            # Remove target file if it exists (might be a link)
            if os.path.exists(ensemble_path_file_target):
                os.remove(ensemble_path_file_target)

            # Create symlink from target to source
            self.logger.info(f'Creating sym link from {ensemble_member} to '
                             f'{ensemble_path_file_target}')
            os.symlink(ensemble_member, ensemble_path_file_target)


# --------------------------------------------------------------------------------------------------
