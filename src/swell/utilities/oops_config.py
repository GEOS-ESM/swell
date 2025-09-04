# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

import os
from collections.abc import Mapping
from abc import ABC, abstractmethod

from swell.utilities.run_jedi_executables import check_obs
from swell.swell_path import get_swell_path

# --------------------------------------------------------------------------------------------------


class OopsConfig(ABC):
    # Abstract class that contains render information for oops configurations

    def __init__(self,
                 jedi_rendering,
                 window_type: str,
                 obs: list,
                 cycle_time: str,
                 jedi_forecast_model: str,
                 observing_system_records_path: str,
                 check_for_obs: bool = True) -> str:

        self.jedi_rendering = jedi_rendering
        self.logger = jedi_rendering.logger
        self.jedi_interface = jedi_rendering.jedi_interface
        self.template_dict = jedi_rendering.__template_dict__

        self.window_type = window_type
        self.obs = obs
        self.cycle_time = cycle_time
        self.jedi_forecast_model = jedi_forecast_model
        self.observing_system_records_path = observing_system_records_path
        self.check_for_obs = check_for_obs

        self.jedi_config_path = os.path.join(get_swell_path(), 'configuration', 'jedi')

    # --------------------------------------------------------------------------------------------------

    # Replicates the behavior of 'SPECIALobservations' in jedi_dictionary_iterator
    # Iterates through observations, render the files, and checks whether to use them
    def special_observations(self) -> Mapping:

        # Output list of observations
        observations = []
        obs_list = self.obs.copy()

        # Iterate through list
        for ob in obs_list:
            # Render the yaml file
            obs_dict = self.jedi_rendering.render_interface_observations(ob)

            # Check whether to use the file, or skip if debugging config file
            if self.check_for_obs:
                use_observation = check_obs(self.observing_system_records_path, ob,
                                            obs_dict, self.cycle_time)
            else:
                use_observation = True

            if use_observation:
                observations.append(obs_dict)
            else:
                self.obs.remove(ob)

        return observations

    # --------------------------------------------------------------------------------------------------

    def interface_model(self, config_name: str) -> Mapping:

        # Pass through to jedi rendering render method
        config_value = self.jedi_rendering.render_interface_model(config_name)

        return config_value

    # --------------------------------------------------------------------------------------------------

    @abstractmethod
    def render_oops(self) -> Mapping:
        return {}

# --------------------------------------------------------------------------------------------------
