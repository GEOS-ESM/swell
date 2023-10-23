# (C) Copyright 2021- United States Government as represented by the Administrator of the
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
        background_time_offset = self.config.background_time_offset()
        crtm_coeff_dir = self.config.crtm_coeff_dir(None)
        observations = self.config.observations()
        window_offset = self.config.window_offset()
        observing_system_records_path = self.config.observing_system_records_path()
        if observing_system_records_path is None:
            cycle_dir = self.config.cycle_dir()
            observing_system_records_path = cycle_dir() + 'observing_system_records'
        experiment_config_path = self.experiment_config_path()
        path_to_configs = os.path.join(experiment_config_path, 'jedi', 'interfaces',
                                       'geos_atmosphere', 'observations')
        cycle_time = os.path.basename(os.path.normpath(cycle_dir))

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
            observation_dict = self.jedi_rendering.render_interface_observations(observation,
                                                                                 observing_system_records_path,
                                                                                 path_to_configs, cycle_time)

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
