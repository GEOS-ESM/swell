# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.tasks.base.task_base import taskBase
from swell.utilities.store_fetch import Store

import os

from r2d2 import R2D2Data

# --------------------------------------------------------------------------------------------------


class SaveObsDiags(taskBase):

    """
    Task to use R2D2 to save obs diag files from experiment to database
    """

    def execute(self):

        # Parse config
        # ------------
        os.environ['R2D2_HOST'] = 'localhost'

        background_time_offset = self.config.background_time_offset()
        crtm_coeff_dir = self.config.crtm_coeff_dir(None)
        observations = self.config.observations()
        window_offset = self.config.window_offset()

        r2d2_store_datastores = self.config.r2d2_fetch_datastores(['swell-r2d2'])
        r2d2_store_datastores = [r.replace("$USER", os.getenv('USER')) for r in r2d2_fetch_datastores]
        limit_store = self.config.limit_r2d2_storing(True)

        # Get window beginning
        window_begin = self.da_window_params.window_begin(window_offset)
        background_time = self.da_window_params.background_time(window_offset,
                                                                background_time_offset)

        # Create templates dictionary
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', crtm_coeff_dir)
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Loop over observation operators
        # -------------------------------
        for observation in observations:

            # Load the observation dictionary
            observation_dict = self.jedi_rendering.render_interface_observations(observation)

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

            file_extension = os.path.splitext(obs_path_file)[1].replace(".", "")

            Store(r2d2_store_datastores,
                  limit_one = limit_store
                  item='observation',
                  source_file=obs_path_file,
                  provider='x0044',
                  observation_type=name,
                  file_extension=file_extension,
                  window_start=window_begin,
                  window_length=window_offset)
