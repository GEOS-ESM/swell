# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import glob
from typing import Union

from swell.tasks.base.task_base import taskBase
from swell.utilities.file_system_operations import move_files

# --------------------------------------------------------------------------------------------------


class MoveEraseForecastRestart(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        """
        Moving restart files (i.e., _checkpoint) to the next cycle geosdir.
        """

        self.logger.info('Moving GEOS restarts for the next forecast cycle')

        # Next cycle folder name
        # -----------------------
        self.forecast_duration = self.config.forecast_duration()

        # Create cycle_dir and RESTART
        # ----------------------------
        if not os.path.exists(self.next_forecast_dir('RESTART')):
            os.makedirs(self.next_forecast_dir('RESTART'), 0o755, exist_ok=True)

        # Move and rename files
        # ----------------------
        self.cycling_restarts()
        self.geos.rename_checkpoints(self.next_forecast_dir())

        # Remove forecast_dir and rename next_forecast_dir to forecast_dir
        # --------------------------------------------------------------
        self.logger.info('Erasing current forecast dir and renaming next forecast dir to it')
        try:
            if os.path.exists(self.forecast_dir()):
                shutil.rmtree(self.forecast_dir())
            os.rename(self.next_forecast_dir(), self.forecast_dir())
        except Exception as e:
            self.logger.abort(f'Failed to move directory: {e}')

    # ----------------------------------------------------------------------------------------------

    def cycling_restarts(self) -> None:

        # Move restarts (checkpoints) in the current cycle dir
        # ------------------------------------------------------
        self.logger.info('GEOS restarts are being moved to the next forecast dir')
        self.logger.info('Finding _checkpoint restarts')

        src = self.forecast_dir('scratch', '*_checkpoint')

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath).split('.')[0]
            move_files(self.logger, filepath, self.next_forecast_dir(filename))

        # Create a dictionary of src/dst for the single files
        # ---------------------------------------------------
        src_dst = {'scratch/tile.bin': '',
                   'scratch/RESTART/iced.nc': 'RESTART',
                   }

        for src, dst in src_dst.items():
            dst = os.path.join(dst, os.path.basename(src))
            move_files(self.logger, self.forecast_dir(src), self.next_forecast_dir(dst))

        # Consider the case of multiple MOM restarts
        # -----------------------------------------------------------------
        src = self.forecast_dir(['scratch', 'RESTART', 'MOM.res*nc'])

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath)
            move_files(self.logger, filepath, self.next_forecast_dir(['FORECAST', filename]))

# --------------------------------------------------------------------------------------------------
