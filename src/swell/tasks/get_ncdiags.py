# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import r2d2
from swell.tasks.base.task_base import taskBase
from swell.utilities.r2d2 import load_r2d2_credentials

# --------------------------------------------------------------------------------------------------


class GetNcdiags(taskBase):

    """
    Task to use R2D2 to obtain ncdiag files from database to experiment directory
    """

    def execute(self) -> None:

        # Load R2D2 credentials
        # ---------------------
        load_r2d2_credentials(
            self.logger,
            self.platform(),
            r2d2_server=self.config.r2d2_server(default=None),
        )

        r2d2_datastore = self.config.r2d2_datastore(default=None)

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

        # Set the JEDI rendering parameters. Model specific ones have None as default
        self.jedi_rendering.add_key('window_begin', window_begin)
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('marine_models', self.config.marine_models(None))

        # Needed for localization templating
        self.jedi_rendering.add_key('suite_to_run', self.config.suite_to_run())

        # Set the observing system records path
        self.jedi_rendering.set_obs_records_path(self.config.observing_system_records_path(None))
        self.jedi_rendering.add_key('crtm_coeff_dir', self.config.crtm_coeff_dir(None))

        # Loop over ncdiag experiments
        # -------------------------------
        for ncdiag_experiment in ncdiag_experiments:

            # Loop over observation operators
            # -------------------------------
            for observation in observations:

                self.logger.info(f"Fetching {observation} for {ncdiag_experiment}")
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

                try:
                    fetch_kwargs = dict(
                        item='feedback',
                        experiment=ncdiag_experiment,
                        observation_type=name,
                        file_extension='nc4',
                        window_start=window_begin,
                        window_length=window_length,
                        target_file=target_file,
                        member=-9999,
                    )
                    if r2d2_datastore:
                        fetch_kwargs['data_store'] = r2d2_datastore
                    r2d2.fetch(**fetch_kwargs)
                except Exception as e:
                    self.logger.info(f'Failed to fetch {target_file}: {str(e)}. Skipping.')
