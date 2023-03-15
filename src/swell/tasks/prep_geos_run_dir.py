# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import shutil, os

from swell.tasks.base.task_base import taskBase


# --------------------------------------------------------------------------------------------------


class PrepGeosRunDir(taskBase):

    def fetch_scratch(self):

        # Folder name contains both horizontal and vertical resolutions
        # ----------------------------
        resolution = self.horizontal_resolution + 'x' + self.vertical_resolution

        # Load experiment file
        # --------------------
        b_dir = os.path.join(self.swell_static_files, 'jedi', 'geos', 'static', 
                            resolution, 'scratch')

        d_dir = os.path.join(self.cycle_dir, 'scratch')

        try:
            self.logger.info('  Copying scratch folder from: '+b_dir)
            shutil.copytree(b_dir, d_dir, dirs_exist_ok=True, symlinks=True)

        except Exception:
            self.logger.abort('Copying scratch failed, see if the folder exists')

    def execute(self):

        """Obtains necessary directories from the Static Swell directory (as 
        defined by 'swell_static_files'):

            - scratch:
            Copies the scratch directory created by the gcm_run.j script,
            right before GEOS run is executed. The scratch directory should 
            match the horizontal and vertical resolutions defined in the 
            forecast_geos suite.

            - TODO GSI:

        Parameters
        ----------
            All inputs are extracted from the JEDI experiment file configuration.
            See the taskBase constructor for more information.
        """

        self.horizontal_resolution = self.config_get('horizontal_resolution')
        self.vertical_resolution = self.config_get('vertical_resolution')
        self.swell_static_files = self.config_get('swell_static_files')
        self.cycle_dir = self.config_get('cycle_dir')
        self.experiment_dir = self.config_get('experiment_dir')

        self.logger.info('Preparing GEOS Forecast directory, copying scratch' +
        ' directory')

        self.fetch_scratch()


# --------------------------------------------------------------------------------------------------
