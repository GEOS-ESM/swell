# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from swell.tasks.base.task_base import taskBase
from r2d2 import fetch


# --------------------------------------------------------------------------------------------------


class GetGeovals(taskBase):

    def execute(self):

        # Parse config
        # ------------
        cycle_dir = self.config_get('cycle_dir')
        geovals_experiment = self.config_get('geovals_experiment')
        geovals_provider = self.config_get('geovals_provider')
        window_begin = self.config_get('window_begin')
        observations = self.config_get('observations')
        window_length = self.config_get('window_length')

        # Loop over observation operators
        # -------------------------------
        for observation in observations:

            # Open the observation operator dictionary
            # ----------------------------------------
            observation_dict = self.open_jedi_interface_obs_config_file(observation)

            # Fetch observation files
            # -----------------------
            target_file = os.path.join(cycle_dir, f'{observation}_geovals.{window_begin}.nc4')
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
