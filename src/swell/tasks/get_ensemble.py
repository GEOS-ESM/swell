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
        """Acquires ensemble member files for a given experiment and cycle

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """
        # Get the path and pattern for the ensemble members
        # -------------------------------------------------
        ensemble_path = self.config.path_to_ensemble()

        # Replate ensemble_path with true path
        # ---------------------------------------------
        ensemble_location = self.cycle_time_dto().strftime(ensemble_path)

        # Fetch list of ensemble members
        # --------------------------------
        ensemble_members = glob.glob(ensemble_location)

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

            # Extract the member name, excluding path
            member_part = member_file.split('/')[-1]

            # Target path and filename
            ensemble_path_file_target = os.path.join(self.cycle_dir(), member_part)

            # Remove target file if it exists (might be a link)
            if os.path.exists(ensemble_path_file_target):
                os.remove(ensemble_path_file_target)

            # Create symlink from target to source
            self.logger.info(f'Creating sym link from {ensemble_member} to '
                             f'{ensemble_path_file_target}')
            os.symlink(ensemble_member, ensemble_path_file_target)


# --------------------------------------------------------------------------------------------------
