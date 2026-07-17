# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import glob
import os
import tarfile

from swell.tasks.base.task_base import taskBase
from swell.utilities.datetime_util import datetime_formats

# --------------------------------------------------------------------------------------------------


class GetEnsemble(taskBase):

    def execute(self) -> None:
        """Acquires marine ensemble member files for a given experiment and cycle.
            Experimental: Currently setup to work only with ocean ensemble members.

            Parameters
            ----------
            All inputs are extracted from the JEDI experiment file configuration.
            See the taskBase constructor for more information.

            Following ADAS/ODAS conventions, the ensemble members are expected to be
            located in directories numbered 001, 002, 003, etc. for each ensemble member. For
            backgrounds files, they will be located under /bkg/001, /bkg/002, /bkg/003, etc.

        """

        # Parse configuration
        # -------------------
        horizontal_resolution = self.config.horizontal_resolution()
        vertical_resolution = self.config.vertical_resolution()
        background_experiment = self.config.background_experiment()

        # Get the path and pattern for the ensemble members
        # -------------------------------------------------
        ensemble_path = self.config.path_to_ensemble()

        # For 3D window, analysis time is the cycle time
        # -------------------------------------------------
        exp_ana_time = self.cycle_time_dto().strftime(datetime_formats['gsi_nc_diag_format'])

        # Define the source tar folder and file
        # -------------------------------------
        ens_tar_file = f'{background_experiment}.mar_ebkg.{exp_ana_time}.tar.gz'
        ens_tar = os.path.join(ensemble_path,
                               f'{horizontal_resolution}x{vertical_resolution}',
                               self.cycle_time_dto().strftime('Y%Y'),
                               ens_tar_file)


        # Link the ensemble tar archive to the cycle directory
        # ------------------------------------------------------
        self.logger.info(f' Linking {self.get_model()} archive file: ' + ens_tar)
        self.geos.linker(ens_tar, ens_tar_file, dst_dir=self.cycle_dir())

        # Drop the suffix from the filename
        ens_tar_folder = os.path.splitext(ens_tar_file)[0]

        # Path to restarts in the cycle directory
        # ---------------------------------------
        cycle_tar = os.path.join(self.cycle_dir(), ens_tar_file)

        #extract the ensemble tar file into /bkg in the cycle directory
        with tarfile.open(cycle_tar) as cycle_tar_file:
            cycle_tar_file.extractall(self.cycle_dir() + "/bkg")

        self.logger.info(f' Extracted {self.get_model()} ensemble files to: ' + self.cycle_dir() 
                         + "/bkg")

# --------------------------------------------------------------------------------------------------
