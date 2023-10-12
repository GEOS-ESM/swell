# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from swell.tasks.base.task_base import taskBase
from swell.utilities.observing_system_records import ObservingSystemRecords

# --------------------------------------------------------------------------------------------------


class GenerateObservingSystemRecords(taskBase):

    def execute(self):

        """
        Generate the observing system channel records from GEOSadas files
        """

        # Parse GSI records and save channel selection yamls
        # --------------------------------------------------
        observations = self.config.observations()
        observing_system_records_path = self.config.observing_system_records_path()
        if observing_system_records_path == 'None':
            cycle_dir = self.config.cycle_dir()
            observing_system_records_path = cycle_dir() + 'observing_system_records'

        path_to_geosana_gridcomp = self.config.observing_system_records_gsi_path()
        if path_to_geosana_gridcomp == 'None':
            path_to_geosana_gridcomp = os.path.join(self.experiment_path(), 'GEOSana_GridComp')
        path_to_gsi_records = os.path.join(path_to_geosana_gridcomp, 'GEOSaana_GridComp', 
                                           'GSI_GridComp', 'mksi', 'sidb')
        sat_records = ObservingSystemRecords()
        sat_records.parse_records(path_to_gsi_records)
        sat_records.save_yamls(observing_system_records_path, observations)

# ----------------------------------------------------------------------------------------------
