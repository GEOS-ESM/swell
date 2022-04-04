# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
from swell.tasks.base.task_base import taskBase
import glob

# --------------------------------------------------------------------------------------------------


class CleanCycle(taskBase):

    """Cleans current cycle based on list defined in the configuration file

       Parameters
       ----------
         All inputs are extracted from the JEDI experiment file configuration.
         See the taskBase constructor for more information.

    """

    def execute(self):

        cfg = self.config
        logger = self.logger
        cycle_dir = self.config.get("cycle_dir")
        clean_list = cfg.get('CLEAN')

        if os.path.isdir(cycle_dir):

            # Remove all specified files
            for pattern in clean_list:
                for file_to_delete in glob.glob(pattern):
                    os.remove(file_to_delete)

            # Save cycle_done file to cycle_dir
            filename = 'cycle_done'
            cmd = 'touch ' + os.path.join(cycle_dir, filename)
            os.system(cmd)
