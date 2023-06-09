# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import shutil
import os
import glob

from swell.tasks.base.task_base import taskBase

from datetime import datetime as dt

# --------------------------------------------------------------------------------------------------


class GetRestart(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        self.logger.info('Obtaining GEOS restarts for the coupled simulation')

        self.swell_static_files = self.config.swell_static_files()

        # Create cycle_dir and INPUT
        # ----------------------------
        if not os.path.exists(self.geos.at_cycle_geosdir('INPUT')):
            os.makedirs(self.geos.at_cycle_geosdir('INPUT'), 0o755, exist_ok=True)

        # *_rst files folder
        # ------------------
        rst_path = self.config.geos_restarts_directory()

        # Restarts should be provided
        # ---------------------------
        self.initial_restarts(rst_path)

    # ----------------------------------------------------------------------------------------------

    def initial_restarts(self, rst_path):

        # GEOS forecast checkpoint files are created in advance
        # ----------------------------------------------------
        # TODO: check tile of restarts here for compatibility?
        # TODO: Users might choose to point to a random local directory, where
        # to keep restart files?
        # -------------------------------------------------------------------
        self.logger.info('GEOS restarts are copied from a previous forecast')

        src = os.path.join(self.swell_static_files, 'geos', 'restarts', rst_path, '*_rst')

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath)
            self.geos.copy_to_geosdir(filepath, self.geos.at_cycle_geosdir(filename))

        src = os.path.join(self.swell_static_files, 'geos', 'restarts', rst_path, 'tile.bin')
        self.geos.copy_to_geosdir(src, self.geos.at_cycle_geosdir('tile.bin'))

        # Consider the case of multiple MOM restarts
        # -------------------------------------------
        src = os.path.join(self.swell_static_files, 'geos', 'restarts', rst_path, 'MOM.res*nc')

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath)
            self.geos.copy_to_geosdir(filepath, self.geos.at_cycle_geosdir(['INPUT', filename]))

# --------------------------------------------------------------------------------------------------
