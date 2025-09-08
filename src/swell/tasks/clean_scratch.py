# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
from swell.tasks.base.task_base import taskBase
import glob
from swell.utilities.shell_commands import run_track_log_subprocess

# --------------------------------------------------------------------------------------------------


class CleanScratch(taskBase):

    """Cleans current cycle based on list defined in the configuration file

       Parameters
       ----------
         All inputs are extracted from the JEDI experiment file configuration.
         See the taskBase constructor for more information.

    """

    def execute(self) -> None:

        if self.config.run_in_scratch():
            scratch_path = self.experiment_path(scratch=True)
            experiment_path = self.experiment_path(scratch=False)

            files = glob.glob(os.path.join(scratch_path, '*'))

            command = ['cp', '-r'] + files + [experiment_path]

            run_track_log_subprocess(self.logger, command)

# --------------------------------------------------------------------------------------------------
