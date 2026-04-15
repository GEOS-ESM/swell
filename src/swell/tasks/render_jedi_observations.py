# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
from ruamel.yaml import YAML

from swell.tasks.base.task_base import taskBase
from swell.tasks.base.task_setup import TaskSetup
from swell.tasks.base.task_attributes import task_attributes
import swell.configuration.question_defaults as qd
from swell.utilities.run_jedi_executables import check_obs

# --------------------------------------------------------------------------------------------------

task_name = 'RenderJediObservations'


@task_attributes.register(task_name)
class Setup(TaskSetup):
    def set_defaults(self):
        self.base_name = task_name
        self.is_cycling = True
        self.model_dep = True
        self.questions = [
            qd.check_for_obs(),
            qd.crtm_coeff_dir(),
            qd.background_time_offset(),
            qd.observing_system_records_path(),
            qd.observations(),
            qd.set_obs_as_local(),
            qd.window_length()
        ]

# --------------------------------------------------------------------------------------------------


class RenderJediObservations(taskBase):

    def execute(self) -> None:

        # List of observations
        obs_list = self.config.observations()

        # Whether to run get_channels for obs
        check_for_obs = self.config.check_for_obs(True)

        # Observing system records paths
        observing_system_records_path = self.config.observing_system_records_path(None)
        self.jedi_rendering.set_obs_records_path(observing_system_records_path)

        # Marine models
        marine_models = self.config.marine_models(None)

        # Window parameters
        window_length = self.config.window_length()
        background_time_offset = self.config.background_time_offset()

        # Window parameters for observations
        window_begin = self.da_window_params.window_begin(window_length)
        background_time = self.da_window_params.background_time(background_time_offset)
        crtm_coeff_dir = self.config.crtm_coeff_dir(None)

        # Set fields for obs files
        self.jedi_rendering.add_key('window_begin', window_begin)
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', crtm_coeff_dir)
        self.jedi_rendering.add_key('marine_models', marine_models)

        cwd = os.getcwd()

        observations = []

        # Iterate through list
        for ob in obs_list:

            # Render the yaml file
            obs_dict = self.jedi_rendering.render_interface_observations(ob)

            obs_dict['observation_name'] = ob

            # Check whether to use the file, or skip if debugging config file
            if check_for_obs:
                use_observation = check_obs(observing_system_records_path, ob,
                                            obs_dict, self.cycle_time)
            else:
                self.logger.info(f'Not checking for obs {ob}')
                use_observation = True

            if use_observation:
                observations.append(obs_dict)

        # Create the output file
        os.chdir(cwd)

        jedi_observations_file = os.path.join(self.cycle_dir(), 'obs.yaml')

        yaml = YAML()
        yaml.default_flow_style = False

        with open(jedi_observations_file, 'w') as f:
            yaml.dump(observations, f)


# --------------------------------------------------------------------------------------------------
