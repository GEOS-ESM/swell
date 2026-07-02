# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
from pathlib import Path

from swell.utilities.build import link_path
from swell.tasks.base.task_base import taskBase
import subprocess


# --------------------------------------------------------------------------------------------------


class CloneSpoc(taskBase):

    def execute(self) -> None:

        # Get the experiment/spoc directory
        # ----------------------------------------
        swell_exp_path = self.experiment_path()
        spoc_exp_path = os.path.join(swell_exp_path, 'spoc')

        spoc_tag = self.config.spoc_tag()
        spoc_source_directory = self.config.spoc_source_directory()

        # Link to spoc source directory, if specified
        # -------------------------------------------
        if spoc_source_directory is not None:
            link_path(spoc_source_directory, spoc_exp_path)
            return
        
        # Construct the clone command
        # ---------------------------
        clone_command = ['git', 'clone', 'https://github.com/GEOS-ESM/spoc.git', '-b',
                         spoc_tag, spoc_exp_path]
        
        # Clone the repo
        # --------------
        subprocess.run(clone_command, check=True)

        self.logger(f'Successfully cloned GEOS-ESM/spoc at branch/tag {spoc_tag}')

# --------------------------------------------------------------------------------------------------
