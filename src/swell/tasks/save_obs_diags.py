# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
from swell.tasks.base.task_base import taskBase
from r2d2 import store
from swell.utilities.r2d2 import create_r2d2_config
from swell.utilities.run_jedi_executables import check_obs

# --------------------------------------------------------------------------------------------------


class SaveObsDiags(taskBase):

    """
    Task to use R2D2 to save obs diag files from experiment to database
    """

    def execute(self) -> None:

        # Parse config
        # ------------
        background_time_offset = self.config.background_time_offset()
        crtm_coeff_dir = self.config.crtm_coeff_dir(None)
        observations = self.config.observations()
        window_offset = self.config.window_offset()
        r2d2_local_path = self.config.r2d2_local_path()

        # Set the observing system records path
        self.jedi_rendering.set_obs_records_path(self.config.observing_system_records_path(None))

        # Get window beginning
        window_begin = self.da_window_params.window_begin(window_offset)
        background_time = self.da_window_params.background_time(window_offset,
                                                                background_time_offset)

        # Create templates dictionary
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', crtm_coeff_dir)
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Set R2D2 config file
        # --------------------
        create_r2d2_config(self.logger, self.platform(), self.cycle_dir(), r2d2_local_path)

        # Loop over observation operators
        # -------------------------------
        for observation in observations:

            # Load the observation dictionary
            observation_dict = self.jedi_rendering.render_interface_observations(observation)

            # Check if observation was used
            use_obs = check_obs(self.jedi_rendering.observing_system_records_path, observation,
                                observation_dict, self.cycle_time_dto())
            if not use_obs:
                continue

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
                  experiment=self.experiment_id())
