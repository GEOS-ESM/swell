# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from datetime import datetime as dt
import os

from swell.tasks.base.task_base import taskBase
from swell.tasks.base.geos_tasks_run_executable_base import *

# --------------------------------------------------------------------------------------------------


class RunGeosExecutable(GeosTasksRunExecutableBase):

    def execute(self):

        # Path to executable being run
        # ----------------------------
        npx_proc = self.config_get('npx_proc', None)  # Used in eval(total_processors)
        npy_proc = self.config_get('npy_proc', None)  # Used in eval(total_processors)
        total_processors = self.config_get('total_processors')

        # Create RESTART folder
        # ---------------------
        if not os.path.exists(self.at_cycle_geosdir('RESTART')):
            os.mkdir(self.at_cycle_geosdir('RESTART'))

        # Output log file
        # ---------------
        output_log_file = self.at_cycle_geosdir('geos_out.log')

        # Compute number of processors
        # ----------------------------
        total_processors = total_processors.replace('npx_proc', str(npx_proc))
        total_processors = total_processors.replace('npy_proc', str(npy_proc))
        np = eval(total_processors)

        # GEOS executable
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

        self.run_executable(self.at_cycle_geosdir(), np, geos_executable_path,
                            geos_modules_path, output_log_file)
        exit()

        #######################################################################
        # Create links for SOCA to read
        # Separate task?
        #######################################################################
        # current_cycle = self.config_get('current_cycle')
        # TODO: Is this a good approach?
        current_cycle = os.path.basename(os.path.dirname(self.cycle_dir()))
        # Leaving here, In get_cycle_dir but this should not be called if the task does not receive model.
        # so major issue is -m argument for geos
        # at_cycle situ

        # Option #1:
        # Link restart to history output
        # TODO: this will only work for 3Dvar
        # ----------------------------------
        # cc_dto = dt.strptime(current_cycle, self.get_datetime_format())
        # src = self.at_cycle_geosdir('his_' + cc_dto.strftime('%Y_%m_%d_%H') + '.nc')

        # Option #2:
        # Link restart to restart
        # GEOS restarts have seconds in their filename
        # TODO: this requires a default if the task is not attached a model (geos_ocean or atm.)
        # -------------------------------------------------------------------------------------
        an_fcst_offset = self.config_get('analysis_forecast_window_offset')
        rst_dto = self.adjacent_cycle(an_fcst_offset, return_date=True)
        seconds = str(rst_dto.hour * 3600 + rst_dto.minute * 60 + rst_dto.second)

        # Generic rst file format for SOCA
        # --------------------------------
        # src = self.at_cycle_geosdir(['RESTART', rst_dto.strftime('MOM.res_Y%Y_D%j_S')
        #                              + seconds + '.nc'])
        src = self.at_cycle_geosdir(['RESTART', 'MOM.res.nc'])
        dst = 'MOM6.res.' + current_cycle + '.nc'

        if os.path.exists(src):
            self.geos_linker(src, dst, dst_dir=self.cycle_dir)

# --------------------------------------------------------------------------------------------------
