# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
from swell.tasks.base.task_base import taskBase

from swell.tasks.base.task_setup import TaskSetup
from swell.tasks.base.task_attributes import task_attributes
import swell.configuration.question_defaults as qd
from swell.utilities.r2d2 import load_r2d2_credentials

# --------------------------------------------------------------------------------------------------

task_name = 'GetNcdiags'


@task_attributes.register(task_name)
class Setup(TaskSetup):
    def set_defaults(self):
        self.base_name = task_name
        self.is_cycling = True
        self.model_dep = True
        self.questions = [
            qd.background_time_offset(),
            qd.crtm_coeff_dir(),
            qd.observations(),
            qd.observing_system_records_path(),
            qd.ncdiag_experiments(),
            qd.marine_models(),
            qd.window_length(),
        ]

# --------------------------------------------------------------------------------------------------


class GetNcdiags(taskBase):

    """
    Task to use R2D2 to obtain ncdiag files from database to experiment directory
    """

    def execute(self) -> None:

        # Import modules
        # --------------
        from r2d2 import fetch

        # Load R2D2 credentials
        # ---------------------
        load_r2d2_credentials(
            self.logger,
            self.platform(),
            r2d2_server=self.config.r2d2_server(default=None),
        )

        # Parse config
        # ------------
        ncdiag_experiments = self.config.ncdiag_experiments()
        observations = self.config.observations()
        window_length = self.config.window_length()
        background_time_offset = self.config.background_time_offset()

        # Compute data assimilation window parameters
        # --------------------------------------------
        window_begin = self.da_window_params.window_begin(window_length)
        background_time = self.da_window_params.background_time(background_time_offset)
        self.jedi_rendering.add_key('window_begin', window_begin)
        self.jedi_rendering.add_key('background_time', background_time)

        # Set the JEDI rendering parameters. Model specific ones have None as default
        self.jedi_rendering.add_key('marine_models', self.config.marine_models(None))

        # Set the observing system records path
        self.jedi_rendering.set_obs_records_path(self.config.observing_system_records_path(None))
        self.jedi_rendering.add_key('crtm_coeff_dir', self.config.crtm_coeff_dir(None))

        # Loop over ncdiag experiments
        # -------------------------------
        for ncdiag_experiment in ncdiag_experiments:

            # Loop over observation operators
            # -------------------------------
            for observation in observations:

                print(f"Fetching {observation} for {ncdiag_experiment}")
                # Load the observation dictionary
                observation_dict = self.jedi_rendering.render_interface_observations(observation)

                # Fetch observation files
                # -----------------------
                name = observation_dict['obs space']['name']
                target_file = os.path.join(self.cycle_dir(),
                                           f'{ncdiag_experiment}.{observation}.' +
                                           f'{window_begin}.nc4')

                # TODO: this is handled badly for now, due to the atmosphere observation yaml names
                # If the model is geos_marine, name is observation
                if self.get_model() == 'geos_marine':
                    name = observation

                fetch(date=window_begin,
                      provider='ncdiag',
                      target_file=target_file,
                      ignore_missing=True,
                      time_window=window_length,
                      obs_type=name,
                      type='ob',
                      experiment=ncdiag_experiment)
