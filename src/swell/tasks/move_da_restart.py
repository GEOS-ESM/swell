# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import glob

from swell.tasks.base.task_base import taskBase
from datetime import datetime as dt

# --------------------------------------------------------------------------------------------------


class MoveDaRestart(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        """
        Moving restart files (i.e., _checkpoint) to the next cycle directory.
        One way is using AGCM.rc checkpoint option. This creates time stamped _checkpoint
        files requiring additional filename handling.

        The reason this is a separate task than MoveForecast is that the use of
        "window_length" will require model argument.
        """

        self.logger.info('Moving GEOS restarts for the next simulation cycle')

        # Next cycle folder name
        # -----------------------
        self.next_cycle_dir = self.geos.adjacent_cycle(self.config.window_length())
        self.next_geosdir = os.path.join(self.next_cycle_dir, 'geosdir')

        # Create cycle_dir and INPUT
        # ----------------------------
        if not os.path.exists(self.at_next_geosdir('INPUT')):
            os.makedirs(self.at_next_geosdir('INPUT'), 0o755, exist_ok=True)

        # Move and rename files
        # ----------------------
        self.cycling_restarts()
        self.geos.rename_checkpoints(self.next_geosdir)

    # ----------------------------------------------------------------------------------------------

    def at_next_geosdir(self, paths):

        # Ensure what we have is a list (paths should be a list)
        # ------------------------------------------------------
        if isinstance(paths, str):
            paths = [paths]

        # Combining list of paths with cycle dir for script brevity
        # ---------------------------------------------------------
        full_path = os.path.join(self.next_geosdir, *paths)
        return full_path

    # ----------------------------------------------------------------------------------------------

    def cycling_restarts(self):

        # Move restarts (checkpoints) in the current cycle dir
        # ------------------------------------------------------
        self.logger.info('GEOS restarts are being moved to the next cycle dir')

        src = self.geos.at_cycle_geosdir('*_checkpoint')

        # This alternate source format corresponds to optional use of Restart Record
        # parameters in AGCM.rc
        # -------------------------------------------------------------------------
        agcm_dict = self.geos.parse_rc(self.geos.at_cycle_geosdir('AGCM.rc'))

        if 'RECORD_FREQUENCY' in agcm_dict:
            an_fcst_offset = self.config.analysis_forecast_window_offset()
            rst_dto = self.geos.adjacent_cycle(an_fcst_offset, return_date=True)

            self.logger.info('Using _checkpoint restarts with timestamps')
            src = self.geos.at_cycle_geosdir(rst_dto.strftime('*_checkpoint.%Y%m%d_%H%Mz.nc4'))

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath).split('.')[0]
            self.geos.move_to_next(filepath, self.at_next_geosdir(filename))

        self.geos.move_to_next(self.geos.at_cycle_geosdir('tile.bin'),
                               self.at_next_geosdir('tile.bin'))

        # Consider the case of multiple MOM restarts
        # TODO: this could/should be forced to be a single file (MOM_input option)
        # so wildcard character can be omitted.
        # -----------------------------------------------------------------
        src = self.geos.at_cycle_geosdir(['RESTART', 'MOM.res*nc'])

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath)
            self.geos.move_to_next(filepath, self.at_next_geosdir(['INPUT', filename]))

# --------------------------------------------------------------------------------------------------
