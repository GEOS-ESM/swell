# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import shutil
import glob

from swell.tasks.base.task_base import taskBase

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

            for file in files:
                shutil.copy(file, experiment_path)

# --------------------------------------------------------------------------------------------------
