# (C) Copyright 2023- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import shutil

from swell.tasks.base.task_base import taskBase
from swell.tasks.base.task_setup import TaskSetup
from swell.tasks.base.task_attributes import task_attributes

# --------------------------------------------------------------------------------------------------

task_name = 'RemoveForecastDir'

@task_attributes.register(task_name)
class Setup(TaskSetup):
    def set_attributes(self):
        self.base_name = task_name
        self.is_cycling = True

# --------------------------------------------------------------------------------------------------


class RemoveForecastDir(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        self.logger.info(f"Removing old forecast directory: {self.forecast_dir()}")
        shutil.rmtree(self.forecast_dir())

# --------------------------------------------------------------------------------------------------
