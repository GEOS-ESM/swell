# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import sys
from swell.tasks.base.task_base import taskBase
from r2d2 import fetch
from swell.utilities.r2d2 import create_r2d2_config
# from swell.utilities.run_jedi_executables import check_obs

# --------------------------------------------------------------------------------------------------


class GetNcdiags(taskBase):

    """
    Task to use R2D2 to obtain ncdiag files from database to experiment directory
    """

    def execute(self) -> None:

        # Parse config
        # ------------
        # background_time_offset = self.config.background_time_offset()
        # crtm_coeff_dir = self.config.crtm_coeff_dir(None)
        ncdiag_experiments = self.config.ncdiag_experiments()
        observations = self.config.observations()
        window_offset = self.config.window_offset()
        r2d2_local_path = self.config.r2d2_local_path()

        # Set the observing system records path
        self.jedi_rendering.set_obs_records_path(self.config.observing_system_records_path(None))
        # self.jedi_rendering.add_key('marine_models', self.config.marine_models(None))

        # Get window beginning
        window_begin = self.da_window_params.window_begin(window_offset)
        print('window_begin', window_begin)
        print('window_begin', window_begin)
        print('window_begin', window_begin)
        print('window_begin', window_begin)
        print('window_begin', window_begin)
        print('window_begin', window_begin)
        print('window_begin', window_begin)
        print(self.cycle_time_dto())
        print(self.cycle_dir())
        # background_time = self.da_window_params.background_time(window_offset,
        #                                                         background_time_offset)

        # Create templates dictionary
        # self.jedi_rendering.add_key('background_time', background_time)
        # self.jedi_rendering.add_key('crtm_coeff_dir', crtm_coeff_dir)
        self.jedi_rendering.add_key('marine_models', self.config.marine_models(None))
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Set R2D2 config file
        # --------------------
        create_r2d2_config(self.logger, self.platform(), self.cycle_dir(), r2d2_local_path)

        # Loop over ncdiag experiments
        # -------------------------------
        for ncdiag_experiment in ncdiag_experiments:

            # Loop over observation operators
            # -------------------------------
            for observation in observations:

                # Load the observation dictionary
                observation_dict = self.jedi_rendering.render_interface_observations(observation)

                # # Check if observation was used, here we don't care about the output
                # use_obs = check_obs(self.jedi_rendering.observing_system_records_path, observation,
                #                     observation_dict, self.cycle_time_dto())
                # if not use_obs:
                #     continue

                # Store observation files
                # -----------------------
                name = observation_dict['obs space']['name']
                obs_path_file = observation_dict['obs space']['obsdataout']['engine']['obsfile']

                # Check for need to add 0000 to the file
                # if not os.path.exists(obs_path_file):
                #     obs_path_file_name, obs_path_file_ext = os.path.splitext(obs_path_file)
                #     obs_path_file_0000 = obs_path_file_name + '_0000' + obs_path_file_ext
                #     if not os.path.exists(obs_path_file_0000):
                #         self.logger.abort(f'No observation file found for {obs_path_file} or ' +
                #                           f'{obs_path_file_0000}')
                #     obs_path_file = obs_path_file_0000

                print('obs_path_file', obs_path_file)
                print('name', name)
                target_file = os.path.join(self.cycle_dir(),
                                           f'{ncdiag_experiment}.{observation}.' +
                                           f'{window_begin}.nc4')

                fetch(date=window_begin,
                    provider='ncdiag',
                    target_file=target_file,
                    ignore_missing=True,
                    obs_type=name,
                    type='ob',
                    experiment=ncdiag_experiment)
