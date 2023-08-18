# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import glob

from swell.tasks.base.task_base import taskBase
from swell.utilities.file_system_operations import move_files

# --------------------------------------------------------------------------------------------------


class MoveDaRestart(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        """
        Moving restart files (i.e., _checkpoint) to the next cycle directory.
        One way is using AGCM.rc checkpoint option. This creates time stamped _checkpoint
        files requiring additional filename handling.

        The reason this is a separate task than MoveForecast is that the use of
        "window_length" will require model argument input.
        """

        self.logger.info('Moving GEOS restarts to the next forecast cycle')
        self.jedi_rendering.add_key('mom6_iau', self.config.mom6_iau(False))

        # Obtain MOM6 IAU bool
        # ----------------------
        self.mom6_iau = self.config.mom6_iau()

        # Next forecast directory
        # -----------------------
        self.next_forecast_dir = self.geos.adjacent_cycle(self.config.window_length())

        # Create cycle_dir and INPUT
        # ----------------------------
        if not os.path.exists(self.at_next_fcst_dir('INPUT')):
            os.makedirs(self.at_next_fcst_dir('INPUT'), 0o755, exist_ok=True)

        # Move and rename files
        # ----------------------
        self.cycling_restarts()
        self.geos.rename_checkpoints(self.next_forecast_dir)

    # ----------------------------------------------------------------------------------------------

    def at_next_fcst_dir(self, paths):

        # Ensure what we have is a list (paths should be a list)
        # ------------------------------------------------------
        if isinstance(paths, str):
            paths = [paths]

        # Combining list of paths with cycle dir for script brevity
        # ---------------------------------------------------------
        full_path = os.path.join(self.next_forecast_dir, *paths)
        return full_path

    # ----------------------------------------------------------------------------------------------

    def cycling_restarts(self):

        # Move restarts (checkpoints) in the current cycle dir
        # ------------------------------------------------------
        self.logger.info('GEOS restarts are being moved to the next forecast dir')

        src = self.forecast_dir('*_checkpoint')

        # This alternate source format corresponds to optional use of Restart Record
        # parameters in AGCM.rc
        # -------------------------------------------------------------------------
        agcm_dict = self.geos.parse_rc(self.forecast_dir('AGCM.rc'))

        if 'RECORD_FREQUENCY' in agcm_dict:
            an_fcst_offset = self.config.analysis_forecast_window_offset()
            rst_dto = self.geos.adjacent_cycle(an_fcst_offset, return_date=True)

            self.logger.info('Using _checkpoint restarts with timestamps')
            src = self.forecast_dir(rst_dto.strftime('*_checkpoint.%Y%m%d_%H%Mz.nc4'))

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath).split('.')[0]
            move_files(self.logger, filepath, self.at_next_fcst_dir(filename))

        move_files(self.logger, self.forecast_dir('tile.bin'),
                   self.at_next_fcst_dir('tile.bin'))

        # PARALLEL_RESTARTFILES in MOM_input should be set to False or multiple
        # restart files will be created and we don't want that
        # ---------------------------------------------------------
        src = []
        src.append(self.forecast_dir(['RESTART', 'MOM.res.nc']))

        if(self.mom6_iau):
            src.append(os.path.join(self.cycle_dir(), 'mom6_increment.nc'))

        for filepath in src:
            filename = os.path.basename(filepath)
            move_files(self.logger, filepath, self.at_next_fcst_dir(['INPUT', filename]))

# --------------------------------------------------------------------------------------------------
