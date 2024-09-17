# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from swell.tasks.base.task_base import taskBase
from swell.utilities.r2d2 import create_r2d2_config
from r2d2 import fetch


# --------------------------------------------------------------------------------------------------

class GetGeovals(taskBase):

    def execute(self) -> None:

        # Parse config
        # ------------
        geovals_experiment = self.config.geovals_experiment()
        geovals_provider = self.config.geovals_provider()
        window_offset = self.config.window_offset()
        background_time_offset = self.config.background_time_offset()
        observations = self.config.observations()
        window_length = self.config.window_length()
        crtm_coeff_dir = self.config.crtm_coeff_dir(None)
        r2d2_local_path = self.config.r2d2_local_path()

        # Get window begin time
        window_begin = self.da_window_params.window_begin(window_offset)
        background_time = self.da_window_params.background_time(window_offset,
                                                                background_time_offset)

        # Set R2D2 config file
        # --------------------
        create_r2d2_config(self.logger, self.platform(), self.cycle_dir(), r2d2_local_path)

        # Add to JEDI template rendering dictionary
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', crtm_coeff_dir)
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Loop over observation operators
        # -------------------------------
        for observation in observations:

            # Fetch observation files
            # -----------------------
            target_file = os.path.join(self.cycle_dir(),
                                       f'{observation}_geovals.{window_begin}.nc4')
            self.logger.info("Processing observation file "+target_file)

            fetch(date=window_begin,
                  target_file=target_file,
                  provider=geovals_provider,
                  obs_type=observation,
                  time_window=window_length,
                  type='ob',
                  experiment=geovals_experiment)

            # Change permission
            os.chmod(target_file, 0o644)

    # ----------------------------------------------------------------------------------------------
