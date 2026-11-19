# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import glob

from swell.tasks.base.task_base import taskBase
from swell.tasks.base.task_setup import TaskSetup
from swell.tasks.base.task_attributes import task_attributes
import swell.configuration.question_defaults as qd
from swell.utilities.file_system_operations import move_files

# --------------------------------------------------------------------------------------------------

task_name = 'MoveForecastRestart'


@task_attributes.register(task_name)
class Setup(TaskSetup):
    def set_defaults(self):
        self.base_name = task_name
        self.is_cycling = True
        self.questions = [
            qd.forecast_duration()
        ]

# --------------------------------------------------------------------------------------------------


class MoveForecastRestart(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:
        """Moves restart files to the next forecast cycle.

        This involves moving _checkpoint files and marine model restarts
        from the scratch directory to the forecast directory, and
        renaming them as necessary.
        """

        self.logger.info('Moving GEOS restarts for the next forecast cycle')

        # Next cycle folder name
        # -----------------------
        self.forecast_duration = self.config.forecast_duration()

        # Create cycle_dir and RESTART
        # ----------------------------
        if not os.path.exists(self.forecast_dir('RESTART')):
            os.makedirs(self.forecast_dir('RESTART'), 0o755, exist_ok=True)

        # Move and rename files in the next forecast directory
        # ----------------------------------------------
        self.move_restarts()
        self.move_marine_restarts()
        self.geos.rename_checkpoints(self.forecast_dir())

    # ----------------------------------------------------------------------------------------------

    def move_restarts(self) -> None:
        """Moves GEOS checkpoint restarts from scratch to the forecast directory."""

        # Move restarts (checkpoints) in the current cycle dir
        # ------------------------------------------------------
        self.logger.info('GEOS restarts are being moved to the next forecast dir')
        self.logger.info('Finding _checkpoint restarts')

        src = self.forecast_dir(['scratch', '*_checkpoint'])

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath).split('.')[0]
            move_files(self.logger, filepath, self.forecast_dir(filename))

    # ----------------------------------------------------------------------------------------------

    def move_marine_restarts(self) -> None:
        """Moves marine model restart files to the next forecast directory."""

        # Create a dictionary of src/dst for the single files
        # ---------------------------------------------------
        src_dst = {'scratch/tile.bin': '',
                   'scratch/RESTART/iced.nc': 'RESTART',
                   }

        for src, dst in src_dst.items():
            dst = os.path.join(dst, os.path.basename(src))
            move_files(self.logger, self.forecast_dir(src), self.forecast_dir(dst))

        # Consider the case of multiple MOM restarts
        # -----------------------------------------------------------------
        src = self.forecast_dir(['scratch', 'RESTART', 'MOM.res*nc'])

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath)
            move_files(self.logger, filepath, self.forecast_dir(['RESTART', filename]))

# --------------------------------------------------------------------------------------------------
