# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import shutil
import os
import glob

from swell.utilities.geos_tasks_run_executable import *
from datetime import datetime as dt

# --------------------------------------------------------------------------------------------------


class MoveRestart(GeosTasksRunExecutable):

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

        src = self.at_cycle_geosdir(self.rst_dto.strftime('*_checkpoint.%Y%m%d_%H%Mz.nc4'))

        # This part ensures forecast GEOS runs even without timestamped restarts
        # ----------------------------------------------------------------------
        if not list(glob.glob(src)):
            self.logger.info('Using _checkpoint restarts without timestamps')
            src = self.at_cycle_geosdir('*_checkpoint')

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath).split('.')[0]
            self.move_to_next(filepath, self.at_next_geosdir(filename))

        self.move_to_next(self.at_cycle_geosdir('tile.bin'), self.at_next_geosdir('tile.bin'))

        # Consider the case of multiple MOM restarts
        # TODO: this could be forced to be a single file (MOM_input option)
        # -----------------------------------------------------------------
        src = self.at_cycle_geosdir(['RESTART', 'MOM.res*nc'])

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath)
            self.move_to_next(filepath, self.at_next_geosdir(['INPUT', filename]))

    # ----------------------------------------------------------------------------------------------

    def move_to_next(self, src_dir, dst_dir):

        try:
            self.logger.info(' Moving file(s) from: '+src_dir)
            shutil.move(src_dir, dst_dir)

        except Exception:
            self.logger.abort('Moving failed, see if source files exist')

    # ----------------------------------------------------------------------------------------------

    def rename_checkpoints(self):

        # Rename _checkpoint files to _rst
        # Move to the next geos cycle directory
        # -------------------------------------
        os.chdir(self.next_geosdir)

        self.logger.info('Renaming *_checkpoint files to *_rst')
        try:
            os.system('rename _checkpoint _rst *_checkpoint')
        except Exception:
            self.logger.abort('Renaming failed, see if checkpoint files exists')

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        """
        Moving correct restart files (i.e., _checkpoint) to the next cycle directory.
        We are using AGCM.rc checkpoint option, which creates time stamped _checkpoint
        files requiring additional filename handling.
        """

        self.logger.info('Moving GEOS restarts for the next simulation cycle')

        self.cycle_dir = self.config_get('cycle_dir')

        # Next cycle folder name
        # -----------------------
        self.window_length = self.config_get('window_length')
        self.next_cycle_dir = self.adjacent_cycle(self.cycle_dir, self.window_length)
        self.next_geosdir = os.path.join(self.next_cycle_dir, 'geosdir')

        # Create cycle_dir and INPUT
        # ----------------------------
        if not os.path.exists(self.at_next_geosdir('INPUT')):
            os.makedirs(self.at_next_geosdir('INPUT'), 0o755, exist_ok=True)

        # GEOS restarts have seconds in their filename
        # TODO: this requires a default if the task is not attached a model (geos_ocean or atm.)
        # -------------------------------------------------------------------------------------
        an_fcst_offset = self.config_get('analysis_forecast_window_offset')
        self.rst_dto = self.adjacent_cycle(self.cycle_dir, an_fcst_offset, return_date=True)

        self.cycling_restarts()
        self.rename_checkpoints()

# --------------------------------------------------------------------------------------------------
