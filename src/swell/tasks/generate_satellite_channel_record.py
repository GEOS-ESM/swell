# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from swell.tasks.base.task_base import taskBase


# --------------------------------------------------------------------------------------------------


class GenerateSatelliteChannelRecord(taskBase):

    def execute(self):

        """
        Generate the satellite channel record from GEOSadas files
        """

        # Parse config
        # ------------
        observations = self.config.observations()

        # Create files like amsua_n19_channel_record.yaml in self.cycle_dir()/satellite_channel_record



# ----------------------------------------------------------------------------------------------
