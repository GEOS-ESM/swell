# (C) Copyright 2021-2023 United States Government as represented by the Administrator of the
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

        cycle_dir = self.config_get("cycle_dir")
        clean_list = self.config_get('clean_patterns', None)

        # If no cleaning requested then exit
        if clean_list is None:
            return

        if os.path.isdir(cycle_dir):
            os.chdir(cycle_dir)
            # Remove all specified files
            for pattern in clean_list:
                if pattern == '*':
                    continue
                path_parts = os.path.split(pattern)
                if path_parts[1] == '*':
                    continue
                else:
                    for file_to_delete in glob.glob(path_parts[1]):
                        os.remove(file_to_delete)

            # Save cycle_done file to cycle_dir
            filename = 'cycle_done'
            cmd = 'touch ' + os.path.join(cycle_dir, filename)
            os.system(cmd)
