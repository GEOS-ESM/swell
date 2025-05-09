# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
from swell.tasks.base.task_base import taskBase
from r2d2 import fetch
from swell.utilities.r2d2 import create_r2d2_config

# --------------------------------------------------------------------------------------------------


class GetNcdiags(taskBase):

    """
    Task to use R2D2 to obtain ncdiag files from database to experiment directory
    """

    def execute(self) -> None:

        # Parse config
        # ------------
        ncdiag_experiments = self.config.ncdiag_experiments()
        observations = self.config.observations()
        window_offset = self.config.window_offset()
        window_length = self.config.window_length()
        r2d2_local_path = self.config.r2d2_local_path()

        # Get window beginning
        window_begin = self.da_window_params.window_begin(window_offset)

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

                # Fetch observation files
                # -----------------------
                name = observation_dict['obs space']['name']
                target_file = os.path.join(self.cycle_dir(),
                                           f'{ncdiag_experiment}.{observation}.' +
                                           f'{window_begin}.nc4')

                fetch(date=window_begin,
                      provider='ncdiag',
                      target_file=target_file,
                      ignore_missing=True,
                      time_window=window_length,
                      obs_type=name,
                      type='ob',
                      experiment=ncdiag_experiment)
