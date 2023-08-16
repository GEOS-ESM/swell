# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import glob

from swell.tasks.base.task_base import taskBase
from swell.utilities.file_system_operations import copy_to_dst_dir

# --------------------------------------------------------------------------------------------------


class GetGeosRestart(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        self.logger.info('Obtaining GEOS restarts for the coupled simulation')

        self.swell_static_files = self.config.swell_static_files()

        # Create forecast_dir and INPUT
        # ----------------------------
        if not os.path.exists(self.forecast_dir('INPUT')):
            os.makedirs(self.forecast_dir('INPUT'), 0o755, exist_ok=True)

        # *_rst files folder
        # ------------------
        rst_path = self.config.geos_restarts_directory()

        # Restarts should be provided
        # ---------------------------
        self.initial_restarts(rst_path)

    # ----------------------------------------------------------------------------------------------

    def initial_restarts(self, rst_path):

        # GEOS forecast checkpoint files are created in advance
        # TODO: check tile of restarts here for compatibility?
        # -------------------------------------------------------------------
        self.logger.info('GEOS restarts are copied from a previous forecast')

        src = os.path.join(self.swell_static_files, 'geos', 'restarts', rst_path, '*_rst')

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath)
            copy_to_dst_dir(self.logger, filepath, self.forecast_dir(filename))

        src = os.path.join(self.swell_static_files, 'geos', 'restarts', rst_path, 'tile.bin')
        copy_to_dst_dir(self.logger, src, self.forecast_dir('tile.bin'))

        # Consider the case of multiple MOM restarts
        # -------------------------------------------
        src = os.path.join(self.swell_static_files, 'geos', 'restarts', rst_path, 'MOM.res*nc')

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath)
            copy_to_dst_dir(self.logger, filepath, self.forecast_dir(['INPUT', filename]))

# --------------------------------------------------------------------------------------------------
