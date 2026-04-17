# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.tasks.base.task_base import taskBase
from swell.tasks.base.task_setup import TaskSetup
from swell.tasks.base.task_attributes import task_attributes
import swell.configuration.question_defaults as qd

from swell.utilities.r2d2 import load_r2d2_credentials

from swell.utilities.run_jedi_executables import check_obs

# --------------------------------------------------------------------------------------------------

task_name = 'SaveObsDiags'


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
            qd.window_length(),
            qd.marine_models()
        ]

# --------------------------------------------------------------------------------------------------


class SaveObsDiags(taskBase):

    """
    Task to use R2D2 to save obs diag files from experiment to database
    """

    def execute(self) -> None:


        # Local import because module is not loaded until experiment launch
        import r2d2

        # Load R2D2 credentials
        # ---------------------
        load_r2d2_credentials(self.logger, self.platform())

        # Parse config
        # ------------
        background_time_offset = self.config.background_time_offset()
        crtm_coeff_dir = self.config.crtm_coeff_dir(None)
        observations = self.config.observations()
        window_length = self.config.window_length()

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

        # Loop over observation operators
        # -------------------------------
        for observation in observations:

            # Load the observation dictionary
            observation_dict = self.jedi_rendering.render_interface_observations(observation)

            # Check if observation was used - this checks INPUT file exists and has data
            input_obs_file = observation_dict['obs space']['obsdatain']['engine']['obsfile']
            self.logger.info(f'Checking input observation file: {input_obs_file}')

            use_obs = check_obs(self.jedi_rendering.observing_system_records_path, observation,
                                observation_dict, self.cycle_time_dto(), input_and_output=True)

            # use_obs is false when obs input file (or feedback file) doesn't exist or is empty.
            # The case when the feedback file is listed in yaml but doesn't exit never happens,
            # as JEDI execution fails when input obs file is missing.

            if not use_obs:
                self.logger.info(f'Empty feedback (obs diag) {input_obs_file} file. Skip saving.')
                continue

            name = observation_dict['obs space']['name']
            obs_path_file = observation_dict['obs space']['obsdataout']['engine']['obsfile']

            self.logger.info(f'Found diagnostic output file: {obs_path_file}')

            # Store to R2D2
            # ---------------

            try:
                r2d2.store(
                    item='feedback',
                    experiment=self.config.r2d2_experiment_id(),
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
