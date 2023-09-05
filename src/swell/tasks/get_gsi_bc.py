# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import glob
import isodate
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
        window_length = self.config.window_length()

        # Time of GSI analysis providing the bias correction coefficients
        # ---------------------------------------------------------------
        gsi_bc_ana_time = self.cycle_time_dto() - isodate.parse_duration(window_length)

        # Replace gsi_bc_location datetime string with the actual datetime
        # --------------------------------------------------------------
        gsi_bc_location = gsi_bc_ana_time.strftime(gsi_bc_location)

        # Get list of matching files
        # --------------------------
        bc_files = glob.glob(gsi_bc_location)

        # Holding directory
        gsi_bc_dir = os.path.join(self.cycle_dir(), 'gsi_bcs')
        os.makedirs(gsi_bc_dir, 0o755, exist_ok=True)

        # Check whether the found file is a tar file
        # ------------------------------------------
        if len(bc_files) == 1 and tarfile.is_tarfile(bc_files[0]):

            self.logger.abort('Support for extracting from tar files needs testing. Not supported')

#            # Extract the tar file
#            bc_tar = tarfile.open(bc_files[0])
#
#            # Loop over files in tar file
#            for bc_tar_file in bc_tar.getnames():
#
#                # If bias file found, extract it
#                if 'bias' in bc_tar_file:
#                    bc_tar.extract(bc_tar_file, gsi_bc_dir)
#
#            # Close file
#            bc_tar.close()
#
#            # Should rename the files to be the same e.g. ana.satbias.date etc

        else:

            # Otherwise just copy all the files
            # ---------------------------------
            for bc_file in bc_files:
                shutil.copy(bc_file, gsi_bc_dir)


# --------------------------------------------------------------------------------------------------
