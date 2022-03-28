# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
from swell.tasks.base.task_base import taskBase

# --------------------------------------------------------------------------------------------------


class CleanCycle(taskBase):

    """
    Task to clean current cycle
    """

    def execute(self):

        # Save cycle_done file to cycle_dir
        cycle_dir = self.config.get("cycle_dir")
        filename = 'cycle_done'
        cmd = 'touch ' + os.path.join(cycle_dir, filename)
        os.system(cmd)
