# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
from ruamel.yaml import YAML

from swell.tasks.base.task_base import taskBase
from swell.utilities.run_jedi_executables import run_executable


# --------------------------------------------------------------------------------------------------


class TaskX(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        # Jedi application name
        # ---------------------
        jedi_application = 'ensmeanvariance'

        # Parse configuration
        # -------------------
        jedi_forecast_model = self.config.jedi_forecast_model(None)
        generate_yaml_and_exit = self.config.generate_yaml_and_exit(False)
        npx_proc = self.config.npx_proc(None)
        npy_proc = self.config.npy_proc(None)
        varx = self.config.varx(None)
# --------------------------------------------------------------------------------------------------
