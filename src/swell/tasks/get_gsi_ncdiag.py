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


class GetGsiNcdiag(taskBase):

    def execute(self):

        # Get the build method
        # --------------------
        gsi_diag_path = self.config.path_to_gsi_diags()

        # Get list of ncdiags to test with
        # --------------------------------
        gsi_diag_path_files_pattern = os.path.join(gsi_diag_path, '*ges*.nc*')
        gsi_diag_path_files = glob.glob(gsi_diag_path_files_pattern)

        # Get cycle dir and create if needed
        # ----------------------------------
        gsi_diag_dir = os.path.join(self.cycle_dir(), 'gsi_ncdiags')
        os.makedirs(gsi_diag_dir, 0o755, exist_ok=True)

        # Copy all the files into the cycle directory
        # -------------------------------------------
        for gsi_diag_path_file in gsi_diag_path_files:

            # File name
            gsi_diag_file = os.path.basename(gsi_diag_path_file)

            self.logger.info(f'Copying {gsi_diag_file}')

            # Copy file
            shutil.copyfile(gsi_diag_path_file, os.path.join(gsi_diag_dir, gsi_diag_file))


# --------------------------------------------------------------------------------------------------
