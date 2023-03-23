# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import glob
import os
import shutil

import gsi_ncdiag.gsi_ncdiag as gsid

from swell.tasks.base.task_base import taskBase


# --------------------------------------------------------------------------------------------------


class GsiNcdiagToIoda(taskBase):

    def execute(self):

        # Parse configuration
        # -------------------
        cycle_dir = self.config_get('cycle_dir')
        observations = self.config_get('observations')

        # Assemble all conventional types from ioda
        # -----------------------------------------
        conv_platforms = gsid.conv_platforms
        all_conv = []
        print(conv_platforms)
        for key in conv_platforms:
            all_conv.append(conv_platforms[key].items())

        print(all_conv)

        # List out the conventional types
        # -------------------------------
        conv_types = ['aircraft', '', '', '', '']

        # Copy all the files into the cycle directory
        # -------------------------------------------
        for observation in observations:

            # File name
            self.logger.info(f'{observation}')
# --------------------------------------------------------------------------------------------------
