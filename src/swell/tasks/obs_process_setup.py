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
import glob
from swell.tasks.base.task_base import taskBase


# --------------------------------------------------------------------------------------------------


class ObsProcessSetup(taskBase):

    def execute(self):

        """Acquires background files from a GEOS experiment. Expects traj files stored in a tarfile

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """


        # Path to ioda-converters install
        # -------------------------------
        # iodabin='/discover/nobackup/drholdaw/JediOpt/src/ioda-bundle/develop/build-gni-impi/bin/'
        iodabin = '/discover/nobackup/drholdaw/JediSwell/bundle/1.0.5/build-intel-impi-release/bin/'

        # Current cycle time (middle of the window)
        # -----------------------------------------
        current_cycle = self.config.get('current_cycle')
        current_cycle_dt = dt.strptime(current_cycle, self.config.dt_format)

        # Hours before middle of window that forecast began
        # -------------------------------------------------
        #forecast_offset = isodate.parse_duration(self.config.get('geos_background_restart_offset'))
        #forecast_rst_dt = current_cycle_dt - forecast_offset

        # Create cycle directory if needed
        # --------------------------------
        cycle_dir = self.config.get('cycle_dir')
        print(cycle_dir)
        if not os.path.exists(cycle_dir):
            os.makedirs(cycle_dir, 0o755, exist_ok=True)
        out_dir = cycle_dir + '/out/'
        os.makedirs(out_dir, 0o755, exist_ok=True)

        # Geos experiment settings
        # ------------------------
        geos_experiment  = self.config.get('geos_experiment')
        obs_dir_template = self.config.get('geos_obs_dir_template')        
        obs_dir = current_cycle_dt.strftime(obs_dir_template)

        # Copy obs files to cycle directory
        # ---------------------------------
        for filepath in list(glob.glob(obs_dir + '/*ges*nc4')):
           #for filename in os.listdir(obs_dir + '/*ges*nc4'):
           #if fnmatchh.fnmatch(filename)
           filename = os.path.basename(filepath)
           os.system('ln -sf ' + filepath + ' ' + cycle_dir + '/' + filename)

        # Run proc_gsi_ncdiag
        # ---------------------------------
        os.system('python ' + iodabin + '/proc_gsi_ncdiag.py -o ' + out_dir + ' ' + cycle_dir)

# --------------------------------------------------------------------------------------------------
