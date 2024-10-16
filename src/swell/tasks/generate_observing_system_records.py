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

    def execute(self) -> None:

        """
        Generate the observing system channel records from GEOS_mksi files
        """

        # This task should only execute for geos_atmosphere
        # -------------------------------------------------
        if self.get_model() != 'geos_atmosphere':
            self.logger.info('Skipping GenerateObservingSystemRecords for: ' + self.get_model())
            return

        # Parse GSI records and save yamls
        # --------------------------------
        observing_system_records_path = self.config.observing_system_records_path(None)
        if observing_system_records_path == 'None':
            cycle_dir = self.cycle_dir()
            observing_system_records_path = os.path.join(cycle_dir, 'observing_system_records')

        path_to_geos_mksi = self.config.observing_system_records_mksi_path()
        if path_to_geos_mksi == 'None':
            path_to_geos_mksi = os.path.join(self.experiment_path(), 'GEOS_mksi')

        # Parse sidb
        # ----------
        record_type = 'channel'
        observations = self.config.observations()
        path_to_gsi_records = os.path.join(path_to_geos_mksi, 'sidb')
        sat_records = ObservingSystemRecords(record_type)
        sat_records.parse_records(path_to_gsi_records)
        sat_records.save_yamls(observing_system_records_path, observations)
        self.logger.info('Completed sidb processing.')

        # Parse ozone.db
        # --------------
        record_type = 'level'
        path_to_gsi_records = os.path.join(path_to_geos_mksi, 'ozinfo.db')
        sat_records = ObservingSystemRecords(record_type)
        sat_records.parse_records(path_to_gsi_records)
        sat_records.save_yamls(observing_system_records_path)
        self.logger.info('Completed ozinfo.db processing')

# ----------------------------------------------------------------------------------------------
