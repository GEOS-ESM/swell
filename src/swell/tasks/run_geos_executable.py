# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os

from swell.tasks.base.task_base import taskBase

# --------------------------------------------------------------------------------------------------


class RunGeosExecutable(taskBase):

    def execute(self):

        # Total number of processors
        # ----------------------------
        np = self.config.total_processors()

        # Create RESTART folder
        # ---------------------
        if not os.path.exists(self.geos.at_cycle_geosdir('RESTART')):
            os.mkdir(self.geos.at_cycle_geosdir('RESTART'))

        # Output log file
        # ---------------
        output_log_file = self.geos.at_cycle_geosdir('geos_out.log')

        # Path to the GEOS executable
        # ---------------
        geos_executable = 'GEOSgcm.x'
        geos_executable_path = os.path.join(self.experiment_path(), 'GEOSgcm', 'build',
                                            'bin', geos_executable)

        # GEOS source
        # ---------------
        geos_modules = 'g5_modules.sh'
        geos_modules_path = os.path.join(self.experiment_path(), 'GEOSgcm', 'source',
                                         '@env', geos_modules)

        # Run the GEOS executable
        # -----------------------
        self.logger.info('Running '+geos_executable_path+' with '+str(np)+' processors.')

        self.geos.run_executable(self.geos.at_cycle_geosdir(), np, geos_executable_path,
                                 geos_modules_path, output_log_file)

# --------------------------------------------------------------------------------------------------
