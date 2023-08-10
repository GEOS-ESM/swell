# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import glob
import os
import shutil
import tarfile

from swell.tasks.base.task_base import taskBase


# --------------------------------------------------------------------------------------------------


class GetGsiBc(taskBase):

    def execute(self):

        # Get the build method
        # --------------------
        gsi_bc_location = self.config.path_to_gsi_bc_coefficients()

        # Holding directory
        gsi_bc_dir = os.path.join(self.cycle_dir(), 'gsi_bcs')
        os.makedirs(gsi_bc_dir, 0o755, exist_ok=True)

        # Get list of bias correction files to copy
        # -----------------------------------------
        files_found = False

        if os.path.isdir(gsi_bc_location):

            # Get list of matching files in the directory
            ana_satbias_rst = glob.glob(os.path.join(gsi_bc_location, '*.ana.satbias.*'))
            ana_satbiaspc_rst = glob.glob(os.path.join(gsi_bc_location, '*.ana.satbiaspc.*'))

            # Record that files were found
            if len(ana_satbias_rst) == 1 and len(ana_satbiaspc_rst) == 1:
                files_found = True

            # Report if too many files were found
            if len(ana_satbias_rst) > 1 or len(ana_satbiaspc_rst) > 1:
                self.logger.abort(f'In GetGsiBc too many files were found in the directory.')

            # Copy files
            shutil.copy(ana_satbias_rst[0], gsi_bc_dir)
            shutil.copy(ana_satbiaspc_rst[0], gsi_bc_dir)

        elif tarfile.is_tarfile(gsi_bc_location):

            bc_tar = tarfile.open(gsi_bc_location)
            found_satbias = False
            found_satbiaspc = False
            for bc_tar_file in bc_tar.getnames():
                if 'ana_satbias_rst' in bc_tar_file:
                    bc_tar.extract(bc_tar_file, gsi_bc_dir)
                    found_satbias = True
                if 'ana_satbiaspc_rst' in bc_tar_file:
                    bc_tar.extract(bc_tar_file, gsi_bc_dir)
                    found_satbiaspc = True
            bc_tar.close()

            # Record that files were found
            if found_satbias and found_satbiaspc:
                files_found = True

        self.logger.assert_abort(files_found, f'When passing \'gsi_bc_location\' it should point '
                                 f'to either a tar file or directory containing *ana_satbias_rst* '
                                 f'and *ana_satbiaspc_rst*. gsi_bc_location = {gsi_bc_location}.')


# --------------------------------------------------------------------------------------------------
