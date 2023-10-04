# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from swell.tasks.base.task_base import taskBase
from swell.utilities.satellite_records import SatelliteRecords

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
        path_to_records = '/discover/nobackup/asewnath/github/GEOSana_GridComp/GEOSaana_GridComp/GSI_GridComp/mksi/sidb/'
        output_dir = self.cycle_dir() + '/satellite_channel_records'
        sat_records = SatelliteRecords()
        sat_records.parse_records(path_to_records)
        sat_records.save_yamls(output_dir, observations)

# ----------------------------------------------------------------------------------------------
