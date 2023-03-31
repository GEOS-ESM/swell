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

        # Parse config
        # ------------
        experiment_id = self.config_get('experiment_id')
        window_begin = self.config_get('window_begin')
        observations = self.config_get('observations')

        # Loop over observation operators
        # -------------------------------
        for observation in observations:

            # Load the observation dictionary
            observation_dict = self.open_jedi_interface_obs_config_file(observation)

            # Store observation files
            # -----------------------
            name = observation_dict['obs space']['name']
            obs_path_file = observation_dict['obs space']['obsdataout']['engine']['obsfile']

            # Check for need to add 0000 to the file
            if not os.path.exists(obs_path_file):
                obs_path_file_name, obs_path_file_ext = os.path.splitext(obs_path_file)
                obs_path_file_0000 = obs_path_file_name + '_0000' + obs_path_file_ext
                if not os.path.exists(obs_path_file_0000):
                    self.logger.abort(f'No observation file found for {obs_path_file} or ' +
                                      f'{obs_path_file_0000}')
                obs_path_file = obs_path_file_0000

            store(date=window_begin,
                  provider='ncdiag',
                  source_file=obs_path_file,
                  obs_type=name,
                  type='ob',
                  experiment=experiment_id)
