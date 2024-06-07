# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from datetime import datetime as dt
import isodate
import os
import tarfile

from swell.tasks.base.task_base import taskBase
from swell.utilities.datetime import datetime_formats

# --------------------------------------------------------------------------------------------------


class GetBackgroundGeosExperiment(taskBase):

    def execute(self):

        """Acquires background files from a previous GEOS-FP experiment. This task
        is specific to a 6-hour DA window and GEOS-FP experiment. Hence, it makes
        certain assumptions about the file structure and naming conventions
        (examples are provided for the x0048 experiment):

            - Background archive file:       x0048.bkgcrst.20211211_15z.tar
            - First background file:         x0048.bkg_clcv_rst.20211211_2100z.nc4
            .
            .
            .
            - Last background file:          x0048.bkg_clcv_rst.20211212_0300z.nc4

        The name of the *bkgcrst.*.tar files correspond to the forecast start time.
        The file names in these tar archives corresponds to the background files
        within the DA window, therefore 7 background files are extracted for a
        6-hour window.

        """

        # Parse config
        # ------------
        background_experiment = self.config.background_experiment()
        geos_fp_background_directory = self.config.geos_fp_background_directory()
        background_time_offset = self.config.background_time_offset()

        # Convert to datetime duration
        # ----------------------------
        background_time_offset_dur = isodate.parse_duration(background_time_offset)

        # Get the background experiment start time
        # -----------------------------------------
        bkgr_exp_start_dto = self.cycle_time_dto()-background_time_offset_dur
        bkgr_exp_start_geos = bkgr_exp_start_dto.strftime(datetime_formats['gsi_nc_diag_format'])

        # Create cycle directory if needed
        # --------------------------------
        if not os.path.exists(self.cycle_dir()):
            os.makedirs(self.cycle_dir(), 0o755, exist_ok=True)

        # Define the source tar folder and file
        # -------------------------------------
        bkgr_tar_file = f'{background_experiment}.bkgcrst.{bkgr_exp_start_geos}.tar'
        bkgr_tar = os.path.join(geos_fp_background_directory,
                                background_experiment,
                                'rs',
                                bkgr_exp_start_dto.strftime('Y%Y'),
                                bkgr_exp_start_dto.strftime('M%m'),
                                bkgr_tar_file)

        # Link the background tar archive to the cycle directory
        # ------------------------------------------------------
        self.logger.info(' Linking GEOS-FP archive file: ' + bkgr_tar)
        self.geos.linker(bkgr_tar, bkgr_tar_file, dst_dir=self.cycle_dir())

        # Path to restarts in the cycle directory
        # ---------------------------------------
        cycle_tar = os.path.join(self.cycle_dir(), bkgr_tar_file)

        # Untar the background files
        # --------------------------
        with tarfile.open(cycle_tar) as cycle_tar_file:
            for member in cycle_tar_file.getmembers():
                if member.isreg():  # Use files only

                    # Extract files
                    # -------------
                    member.name = os.path.basename(member.name)
                    cycle_tar_file.extract(member, self.cycle_dir())

                    # Get the date information from the filename (example):
                    # x0048.bkg_clcv_rst.20211211_2100z.nc4
                    # Strip the filename to get the date information
                    # -----------------------------------------------------
                    member_date_str = member.name.split('.')[2]
                    member_date_dto = dt.strptime(member_date_str, '%Y%m%d_%H00z')

                    # Create the JEDI bkgr filename
                    # -----------------------------
                    jedi_date = member_date_dto.strftime(datetime_formats["directory_format"])
                    bkg_filename_jedi = f'bkg.{jedi_date}.nc4'

                    # Rename the files
                    # ----------------
                    self.logger.info(' Renaming GEOS-FP bkgr from: ' + member.name +
                                     ' to: ' + bkg_filename_jedi)
                    os.rename(os.path.join(self.cycle_dir(), member.name),
                              os.path.join(self.cycle_dir(), bkg_filename_jedi))

# --------------------------------------------------------------------------------------------------
