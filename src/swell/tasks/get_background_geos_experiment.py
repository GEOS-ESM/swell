# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
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


# --------------------------------------------------------------------------------------------------


class GetBackgroundGeosExperiment(taskBase):

    def execute(self):

        """Acquires background files from a GEOS experiment. Expects traj files stored in a tarfile

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """

        # Current cycle time (middle of the window)
        # -----------------------------------------
        current_cycle = self.config.get('current_cycle')
        current_cycle_dt = dt.strptime(current_cycle, self.config.dt_format)

        # Hours before middle of window that forecast began
        # -------------------------------------------------
        forecast_offset = isodate.parse_duration(self.config.get('geos_background_restart_offset'))
        forecast_rst_dt = current_cycle_dt - forecast_offset

        # Create cycle directory if needed
        # --------------------------------
        cycle_dir = self.config.get('cycle_dir')
        if not os.path.exists(cycle_dir):
            os.makedirs(cycle_dir, 0o755, exist_ok=True)

        # Geos experiment settings
        # ------------------------
        geos_experiment = self.config.get('geos_experiment')
        tar_filename_template_geos = self.config.get('geos_bkg_tar_filename_template')
        bkg_filename_template_geos = self.config.get('geos_bkg_filename_template')
        bkg_filename_template_jedi = self.config.get('jedi_bkg_filename_template')

        # Path to restarts
        # ----------------
        traj_tar = forecast_rst_dt.strftime(tar_filename_template_geos)

        # Untar the trajectory file
        # -------------------------
        with tarfile.open(traj_tar) as traj_tar_file:
            for member in traj_tar_file.getmembers():
                if member.isreg():  # Only files

                    # Extract files
                    # -------------
                    member.name = os.path.basename(member.name)
                    traj_tar_file.extract(member, cycle_dir)

                    # Rename the files
                    # ----------------
                    bkg_filename_dt = dt.strptime(member.name, bkg_filename_template_geos)
                    bkg_filename_jedi = bkg_filename_dt.strftime(bkg_filename_template_jedi)
                    os.rename(os.path.join(cycle_dir, member.name),
                              os.path.join(cycle_dir, bkg_filename_jedi))


# --------------------------------------------------------------------------------------------------
