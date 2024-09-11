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


class MoveForecastRestart(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        """
        Moving restart files (i.e., _checkpoint) to the next cycle geosdir.
        """

        self.logger.info('Moving GEOS restarts for the next forecast cycle')

        # Next cycle folder name
        # -----------------------
        self.forecast_duration = self.config.forecast_duration()
        self.next_forecast_dir = self.geos.adjacent_cycle(self.forecast_duration)

        # Create cycle_dir and INPUT
        # ----------------------------
        if not os.path.exists(self.at_next_fcst_dir('INPUT')):
            os.makedirs(self.at_next_fcst_dir('INPUT'), 0o755, exist_ok=True)

        # Move and rename files
        # ----------------------
        self.cycling_restarts()
        self.geos.rename_checkpoints(self.next_forecast_dir)

    # ----------------------------------------------------------------------------------------------

    def at_next_fcst_dir(self, paths: Union[str, list]) -> str:

        # Ensure what we have is a list (paths should be a list)
        # ------------------------------------------------------
        if isinstance(paths, str):
            paths = [paths]

        # Combining list of paths with cycle dir for script brevity
        # ---------------------------------------------------------
        full_path = os.path.join(self.next_forecast_dir, *paths)
        return full_path

    # ----------------------------------------------------------------------------------------------

    def cycling_restarts(self) -> None:

        # Move restarts (checkpoints) in the current cycle dir
        # ------------------------------------------------------
        self.logger.info('GEOS restarts are being moved to the next forecast dir')
        self.logger.info('Finding _checkpoint restarts')

        src = self.forecast_dir('*_checkpoint')

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath).split('.')[0]
            move_files(self.logger, filepath, self.at_next_fcst_dir(filename))

        # Create a dictionary of src/dst for the single files
        # ---------------------------------------------------
        src_dst = {'tile.bin': '',
                   'RESTART/iced.nc': 'INPUT',
                   }

        for src, dst in src_dst.items():
            dst = os.path.join(dst, os.path.basename(src))
            move_files(self.logger, self.forecast_dir(src), self.at_next_fcst_dir(dst))

        # Consider the case of multiple MOM restarts
        # TODO: this could be forced to be a single file (MOM_input option)
        # so wildcard character can be omitted.
        # -----------------------------------------------------------------
        src = self.forecast_dir(['RESTART', 'MOM.res*nc'])

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath)
            move_files(self.logger, filepath, self.at_next_fcst_dir(['INPUT', filename]))

# --------------------------------------------------------------------------------------------------
