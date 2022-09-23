# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
from swell.tasks.base.task_base import taskBase
from r2d2 import store

# --------------------------------------------------------------------------------------------------


class SaveObsDiags(taskBase):

    """
    Task to use R2D2 to save obs diag files from experiment to database
    """

    def execute(self):

        cfg = self.config
        logger = self.logger

        # Parse config
        # ------------
        experiment = cfg.get('experiment_id')
        window_begin = cfg.get('window_begin')
        background_time = cfg.get('background_time')
        obs = cfg.get('OBSERVATIONS')

        # Loop over observation operators
        # -------------------------------
        for ob in obs:

            # Store observation files
            # -----------------------
            name = ob['obs space']['name']
            source_file = ob['obs space']['obsdataout']['engine']['obsfile']

            store(date=window_begin,
                  provider='ncdiag',
                  source_file=source_file,
                  obs_type=name,
                  type='ob',
                  experiment=experiment)
