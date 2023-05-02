# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import shutil
import os
import glob

from swell.tasks.base.geos_tasks_run_executable_base import *
from datetime import datetime as dt

# --------------------------------------------------------------------------------------------------


class MoveRestart(GeosTasksRunExecutableBase):

    # ----------------------------------------------------------------------------------------------

    def at_next_cycle(self, paths):

        # Ensure what we have is a list (paths should be a list)
        # ------------------------------------------------------
        if isinstance(paths, str):
            paths = [paths]

        # Combining list of paths with cycle dir for script brevity
        # ---------------------------------------------------------
        full_path = os.path.join(self.next_cycle_dir, *paths)
        return full_path

    # ----------------------------------------------------------------------------------------------

    def cycling_restarts(self):

        # Get restarts (checkpoints) from the previous cycle dir
        # ------------------------------------------------------
        self.logger.info('GEOS restarts will be moved to the next cycle dir')

        src = self.at_cycle('*_checkpoint')

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath)
            self.move_to_next(filepath, self.at_next_cycle(filename))

        self.move_to_next(self.at_cycle('tile.bin'), self.at_next_cycle('tile.bin'))

        # Consider the case of multiple MOM restarts
        # -------------------------------------------
        src = self.at_cycle(['RESTART', 'MOM.res*nc'])

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath)
            self.move_to_next(filepath, self.at_next_cycle(['INPUT', filename]))

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
        # --------------------------------

        # Move to the cycle directory
        # ---------------------------
        os.chdir(self.next_cycle_dir)

        self.logger.info('Renaming *_checkpoint files to *_rst')
        try:
            os.system('rename _checkpoint _rst *_checkpoint')
        except Exception:
            self.logger.abort('Renaming failed, see if checkpoint files exists')

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        self.logger.info('Moving GEOS restarts for the next simulation cycle')

        self.cycle_dir = self.config_get('cycle_dir')

        # Next cycle folder name
        # -----------------------
        self.window_length = self.config_get('window_length')
        self.next_cycle_dir = self.adjacent_cycle(self.cycle_dir, self.window_length)

        # Create cycle_dir and INPUT
        # ----------------------------
        if not os.path.exists(self.at_next_cycle('INPUT')):
            os.makedirs(self.at_next_cycle('INPUT'), 0o755, exist_ok=True)

        self.cycling_restarts()
        self.rename_checkpoints()

# --------------------------------------------------------------------------------------------------
