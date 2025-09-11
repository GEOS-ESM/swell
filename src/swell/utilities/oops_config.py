# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

import os
from collections.abc import Mapping
from abc import ABC, abstractmethod
from ruamel.yaml import YAML

from swell.swell_path import get_swell_path

# --------------------------------------------------------------------------------------------------


class OopsConfig(ABC):
    # Abstract class that contains render information for oops configurations

    def __init__(self,
                 jedi_rendering,
                 window_type: str,
                 cycle_time: str,
                 cycle_dir: str,
                 jedi_forecast_model: str,
                 observing_system_records_path: str) -> str:

        self.jedi_rendering = jedi_rendering
        self.logger = jedi_rendering.logger
        self.jedi_interface = jedi_rendering.jedi_interface
        self.template_dict = jedi_rendering.__template_dict__

        self.window_type = window_type
        self.cycle_time = cycle_time
        self.cycle_dir = cycle_dir
        self.jedi_forecast_model = jedi_forecast_model
        self.observing_system_records_path = observing_system_records_path

        self.jedi_config_path = os.path.join(get_swell_path(), 'configuration', 'jedi')

    # --------------------------------------------------------------------------------------------------

    def special_observations(self) -> Mapping:

        jedi_observations_file = os.path.join(self.cycle_dir, 'obs.yaml')

        yaml = YAML(typ='safe')

        with open(jedi_observations_file, 'r') as f:
            observations = yaml.load(f)

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
