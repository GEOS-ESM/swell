# (C) Copyright 2021- United States Government as represented by the Administrator of the
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


class GetRestart(GeosTasksRunExecutableBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        self.logger.info('Obtaining GEOS restarts for the coupled simulation')

        self.swell_static_files = self.config_get('swell_static_files', None)

        # Create cycle_dir and INPUT
        # ----------------------------
        if not os.path.exists(self.at_cycle_geosdir('INPUT')):
            os.makedirs(self.at_cycle_geosdir('INPUT'), 0o755, exist_ok=True)

        # *_rst files folder
        # ------------------
        rst_path = self.config_get('geos_restarts_directory')

        # Add config to template rendering dictionary
        # -------------------------------------------
        self.jedi_rendering.add_key('swell_static_files', self.swell_static_files)

        # Restarts should be provided
        # ---------------------------
        self.initial_restarts(rst_path)

    # ----------------------------------------------------------------------------------------------

    def initial_restarts(self, rst_path):

        # GEOS forecast checkpoint files are created in advance
        # ----------------------------------------------------

        # TODO: check tile of restarts here for compatibility?
        # TODO: IMPORTANT! restart folder placement, geos_ocean right now.
        #       also users might choose to point to a random local directory
        # -------------------------------------------------------------------
        self.logger.info('GEOS restarts from a forecast run')

        src = os.path.join(self.swell_static_files, 'jedi', 'interfaces',
                           'geos_ocean', 'model',  'geos', rst_path, '*_rst')

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath)
            self.copy_to_geosdir(filepath, self.at_cycle_geosdir(filename))

        src = os.path.join(self.swell_static_files, 'jedi', 'interfaces',
                           'geos_ocean', 'model', 'geos', rst_path, 'tile.bin')
        self.copy_to_geosdir(src, self.at_cycle_geosdir('tile.bin'))

        # Consider the case of multiple MOM restarts
        # -------------------------------------------
        src = os.path.join(self.swell_static_files, 'jedi', 'interfaces',
                           'geos_ocean', 'model', 'geos', rst_path, 'MOM.res*nc')

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath)
            self.copy_to_geosdir(filepath, self.at_cycle_geosdir(['INPUT', filename]))

# --------------------------------------------------------------------------------------------------
