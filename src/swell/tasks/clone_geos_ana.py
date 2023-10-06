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


class CloneGeosAna(taskBase):

    def execute(self):

        """
        Generate the satellite channel record from GEOSadas files
        """

        # Parse config
        # ------------
        path_to_geosana_gridcomp = self.config.observing_system_records_gsi_path()

        # If observing_system_records_gsi_path is None, clone GEOSana_GridComp repo to experiment
        # directory
        if observing_system_records_gsi_path is None:
            # Clone GEOSana_GridComp develop repo to experiment directory
            os.system('git clone https://github.com/GEOS-ESM/GEOSana_GridComp.git '
                      + os.path.join(self.experiment_path() + 'GEOSana_GridComp'))
        else:
            # Link the source code directory
            link_path(self.config.observing_system_records_gsi_path(),
                      os.path.join(self.experiment_path() + 'GEOSana_GridComp'))


# ----------------------------------------------------------------------------------------------
