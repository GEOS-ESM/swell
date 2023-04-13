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

        # Parse config
        cycle_dir = self.config_get("cycle_dir")
        clean_list = self.config_get('clean_patterns', None)

        # If no cleaning requested then exit
        if clean_list is None:
            return

        # Move to the cycle directory
        os.chdir(cycle_dir)

        # Remove all specified files
        for pattern in clean_list:

            # ---------------------------
            # Perform some safety checks:
            # ---------------------------

            # 1. Check that path is not absolute. Things can only be deleted relative to the cycle
            #    directory.
            if os.path.isabs(pattern):
                self.logger.abort(f'Absolute paths are forbidden. Offending entry: {pattern}')

            # 2. Check that the pattern does not begin with a / or ./
            if pattern[0] == '/' or pattern[0] == '.':
                self.logger.abort(f'Patterns beginning with \'/\' or \'.\' are forbidden. '
                                  f'Offending entry: {pattern}')

            # 3. Check that the pattern is not a blanket removal of all files
            if any(ele == '*' for ele in os.path.split(pattern)):
                self.logger.abort(f'Deleting all files from any directory is forbidden. Offending '
                                  f'entry: {pattern}')

            # ---------------------------
            # ---------------------------

            # Assemble list of files to remove
            items_to_remove = glob.glob(pattern)

            # Loop over files and remove
            for item_to_remove in items_to_remove:

                # Print info about what will be removed
                self.logger.info(f'Removing item {item_to_remove}')

                # Only allow removing of empty directories
                if os.path.isdir(item_to_remove):

                    if len(os.listdir(item_to_remove)) == 0:
                        os.rmdir(item_to_remove)
                    else:
                        self.logger.info(f'Trying to remove directory {item_to_remove} but code '
                                         f'can only remove empty directories. Reorder removal '
                                         f'to empty directory first.')

                else:

                    os.remove(item_to_remove)

        # Save cycle_done file to cycle_dir
        with open(os.path.join(cycle_dir, 'cycle_done'), 'w') as fp:
            pass
