# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os

from swell.tasks.base.task_base import taskBase
from swell.tasks.base.geos_tasks_run_executable_base import *

# --------------------------------------------------------------------------------------------------


class RunGeosExecutable(GeosTasksRunExecutableBase):

    def execute(self):

        # Path to executable being run
        # ----------------------------
        self.cycle_dir = self.config_get('cycle_dir')
        experiment_dir = self.config_get('experiment_dir')
        npx_proc = self.config_get('npx_proc')  # Used in eval(total_processors)
        npy_proc = self.config_get('npy_proc')  # Used in eval(total_processors)
        total_processors = self.config_get('total_processors')

        # Create RESTART folder
        # ---------------------
        if not os.path.exists(self.at_cycle('RESTART')):
            os.mkdir(self.at_cycle('RESTART'))

        # Output log file
        # ---------------
        output_log_file = self.at_cycle('geos_out.log')

        # Compute number of processors
        # ----------------------------
        total_processors = total_processors.replace('npx_proc', str(npx_proc))
        total_processors = total_processors.replace('npy_proc', str(npy_proc))
        np = eval(total_processors)

        # GEOS executable
        # ---------------
        geos_executable = 'GEOSgcm.x'
        geos_executable_path = os.path.join(experiment_dir, 'GEOSgcm', 'build',
                                            'bin', geos_executable)

        # GEOS source
        # ---------------
        geos_modules = 'g5_modules.sh'
        geos_modules_path = os.path.join(experiment_dir, 'GEOSgcm', 'source',
                                         '@env', geos_modules)

        # Run the GEOS executable
        # -----------------------
        self.run_executable(self.cycle_dir, np, geos_executable_path, geos_modules_path, output_log_file)
        self.logger.info('Running '+geos_executable_path+' with '+str(np)+' processors.')

        # Clear the previous INPUT folder
        # -------------------------------
        if os.path.exists(self.at_cycle('INPUT')):
            shutil.rmtree(self.at_cycle('INPUT'))

        # Link restart to history output
        # TODO: this will only work for 3Dvar
        # ------------------------------
        src = self.at_cycle('his_2021_06_21_06.nc')
        dst = self.at_cycle('MOM6.res.20210621T060000Z.nc')

        if os.path.exists(src):
            self.geos_linker(src, dst)

# --------------------------------------------------------------------------------------------------
