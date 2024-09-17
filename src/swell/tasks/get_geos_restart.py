# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import glob

from swell.tasks.base.task_base import taskBase
from swell.utilities.file_system_operations import copy_to_dst_dir, check_if_files_exist_in_path

# --------------------------------------------------------------------------------------------------


class GetGeosRestart(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        self.logger.info('Obtaining GEOS restarts for the coupled simulation')

        swell_static_files_user = self.config.swell_static_files_user(None)
        self.swell_static_files = self.config.swell_static_files()

        # Use static_files_user if present in config and contains files
        # -------------------------------------------------------------
        if swell_static_files_user is not None:
            self.logger.info('swell_static_files_user specified, checking for files')
            if check_if_files_exist_in_path(self.logger, swell_static_files_user):
                self.logger.info(f'Using swell static files in {swell_static_files_user}')
                self.swell_static_files = swell_static_files_user

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

    def initial_restarts(self, rst_path: str) -> None:

        # GEOS forecast checkpoint files are created in advance
        # TODO: check tile of restarts here for compatibility?
        # -------------------------------------------------------------------
        self.logger.info('GEOS restarts are copied from a previous forecast')

        src = os.path.join(self.swell_static_files, 'geos', 'restarts', rst_path, '*_rst')

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath)
            copy_to_dst_dir(self.logger, filepath, self.forecast_dir(filename))

        # Create a dictionary of src/dst for the single files
        # ---------------------------------------------------
        src_dst = {'tile.bin': '',
                   'iced.nc': 'INPUT',
                   }

        for src, dst in src_dst.items():
            dst = os.path.join(dst, src)
            copy_to_dst_dir(self.logger, os.path.join(self.swell_static_files, 'geos', 'restarts',
                                                      rst_path, src), self.forecast_dir(dst))

        # Consider the case of multiple MOM restarts
        # -------------------------------------------
        src = os.path.join(self.swell_static_files, 'geos', 'restarts', rst_path, 'MOM.res*nc')

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath)
            copy_to_dst_dir(self.logger, filepath, self.forecast_dir(['INPUT', filename]))

# --------------------------------------------------------------------------------------------------
