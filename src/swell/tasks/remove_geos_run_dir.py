# (C) Copyright 2023- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import shutil

from swell.tasks.base.task_base import taskBase
from swell.tasks.base.geos_tasks_run_executable_base import *


# --------------------------------------------------------------------------------------------------


class RemoveGeosRunDir(GeosTasksRunExecutableBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        self.cycle_dir = self.config_get('cycle_dir')
        self.logger.info(f"Removing old GEOS directory: {self.at_cycle_geosdir()}")
        shutil.rmtree(self.at_cycle_geosdir())

# --------------------------------------------------------------------------------------------------
