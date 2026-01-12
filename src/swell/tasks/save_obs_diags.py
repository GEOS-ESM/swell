# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os

from swell.tasks.base.task_base import taskBase
from swell.tasks.base.task_setup import TaskSetup
from swell.utilities.question_defaults import QuestionDefaults as qd
from swell.utilities.r2d2 import create_r2d2_config
from swell.utilities.run_jedi_executables import check_obs

# --------------------------------------------------------------------------------------------------

class SaveObsDiags(TaskSetup):
    def set_attributes(self):
        self.is_cycling = True
        self.is_model = True
        self.questions = [
            qd.background_time_offset(),
            qd.crtm_coeff_dir(),
            qd.observations(),
            qd.observing_system_records_path(),
            qd.r2d2_local_path(),
            qd.window_length(),
            qd.marine_models()
        ]

# --------------------------------------------------------------------------------------------------

class SaveObsDiags(taskBase):

    """
    Task to use R2D2 to save obs diag files from experiment to database
    """

    def execute(self) -> None:

        import r2d2

        # Parse config
        # ------------
        background_time_offset = self.config.background_time_offset()
        crtm_coeff_dir = self.config.crtm_coeff_dir(None)
        observations = self.config.observations()
        window_length = self.config.window_length()
        r2d2_local_path = self.config.r2d2_local_path()

        # Set the observing system records path
        self.jedi_rendering.set_obs_records_path(self.config.observing_system_records_path(None))
        self.jedi_rendering.add_key('marine_models', self.config.marine_models(None))

        # Get window beginning
        window_begin = self.da_window_params.window_begin(window_length)  # dto
        background_time = self.da_window_params.background_time(background_time_offset)

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

            # Check if observation was used - this checks INPUT file exists and has data
            input_obs_file = observation_dict['obs space']['obsdatain']['engine']['obsfile']
            self.logger.info(f'Checking input observation file: {input_obs_file}')

            use_obs = check_obs(self.jedi_rendering.observing_system_records_path, observation,
                                observation_dict, self.cycle_time_dto())

            self.logger.info(f'Checking observation {observation}: use_obs = {use_obs}')

            if not use_obs:
                self.logger.info(f'Input observation file analysis for {observation}:')
                self.logger.info(f'  Expected file: {input_obs_file}')
                # Check if file exists and is readable
                # ---------------------------------------
                try:
                    import netCDF4 as nc
                    dataset = nc.Dataset(input_obs_file, 'r')
                    dims = {dim_name: dim.size for dim_name, dim in dataset.dimensions.items()}
                    self.logger.info(f'  File exists but dimensions: {dims}')
                    dataset.close()
                except Exception as e:
                    self.logger.info(f'  File exists but error reading: {str(e)}')

                self.logger.info(f'  Skipping {observation}')
                continue

            # Store diagnostic/feedback files produced by JEDI executables
            # (e.g., variational, hofx, localensembleda).
            # --------------------------------------------------------------

            name = observation_dict['obs space']['name']
            obs_path_file = observation_dict['obs space']['obsdataout']['engine']['obsfile']

            self.logger.info(f'Looking for diagnostic output file: {obs_path_file}')

            # Check for need to add 0000 to the file
            if not os.path.exists(obs_path_file):
                obs_path_file_name, obs_path_file_ext = os.path.splitext(obs_path_file)
                obs_path_file_0000 = obs_path_file_name + '_0000' + obs_path_file_ext
                self.logger.info(f'Primary file not found, checking: {obs_path_file_0000}')

                if not os.path.exists(obs_path_file_0000):
                    self.logger.info(f'Diagnostic output files not found for {observation}:')
                    self.logger.info(f'  Expected: {obs_path_file}')
                    self.logger.info(f'  Expected: {obs_path_file_0000}')
                    self.logger.info(f'  RunJediVariationalExecutable did not run successfully')
                    self.logger.info(f'  Skipping storage of {observation} diagnostic file')
                    continue
                obs_path_file = obs_path_file_0000

            self.logger.info(f'Found diagnostic output file: {obs_path_file}')

            # Store to R2D2
            # ---------------

            try:
                r2d2.store(
                    item='feedback',
                    experiment=self.experiment_id(),
                    observation_type=name,
                    file_extension=obs_path_file.split('.')[-1],
                    window_length='PT6H',
                    window_start=window_begin,
                    source_file=obs_path_file,
                    member=-9999,
                )
                self.logger.info(f'Successfully stored feedback file for {observation}')

            except Exception as e:
                self.logger.info(f'Failed to store feedback file for {observation}: {str(e)}')
                # Don't abort - continue with other observations
                continue
