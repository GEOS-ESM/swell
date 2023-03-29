# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import shutil
import os
import glob

from swell.tasks.base.geos_tasks_run_executable_base import *
from datetime import datetime as dt

# --------------------------------------------------------------------------------------------------


class GetRestart(GeosTasksRunExecutableBase):

    def cycling_restarts(self):

        # Get restarts (checkpoints) from the previous cycle dir 
        # ------------------------------------------------------
        self.logger.info('GEOS restarts will be taken from the previous cycle')

        src = os.path.join(self.previous_cycle_dir, '*_checkpoint')

        for filepath in list(glob.glob(src)):            
            filename = os.path.basename(filepath)
            self.logger.info(' Copying file: ' + filepath)
            shutil.copy(filepath, os.path.join(self.cycle_dir,filename))

        src = os.path.join(self.previous_cycle_dir, 'tile.bin')
    
        self.logger.info(' Copying file: ' + src)
        shutil.copy(src, os.path.join(self.cycle_dir,'tile.bin'))

        src = os.path.join(self.previous_cycle_dir, 'RESTART', 'MOM.res.nc')

        self.logger.info(' Copying file: ' + src)
        shutil.copy(src, os.path.join(self.cycle_dir,'INPUT', 'MOM.res.nc'))

    def initial_restarts(self):

        # GEOS forecast checkpoint files should be created
        # ------------------------------------------------

        # TODO: !!!!!!! check tile of restarts here for compatibility
        # ----------------------------------------------------
        self.logger.info('GEOS restarts from a forecast run')

        src = os.path.join(self.swell_static_files, 'geos', 'static', 
                            'rst_20210630_060000_72x36x50/*_rst')

        for filepath in list(glob.glob(src)):            
            filename = os.path.basename(filepath)
            self.logger.info(' Copying file: ' + filepath)
            shutil.copy(filepath, os.path.join(self.cycle_dir,filename))

        src = os.path.join(self.swell_static_files, 'geos', 'static', 
                            'rst_20210630_060000_72x36x50/tile.bin')
    
        self.logger.info(' Copying file: ' + src)
        shutil.copy(src, os.path.join(self.cycle_dir,'tile.bin'))

        src = os.path.join(self.swell_static_files, 'geos', 'static', 
                            'rst_20210630_060000_72x36x50/MOM.res.nc')
    
        self.logger.info(' Copying file: ' + src)
        shutil.copy(src, os.path.join(self.cycle_dir,'INPUT', 'MOM.res.nc'))

    def rename_checkpoints(self):

        # Rename _checkpoint files to _rst
        # --------------------------------

        # Move to the cycle directory
        # ---------------------------
        os.chdir(self.cycle_dir)

        self.logger.info('Renaming *_checkpoint files to *_rst')
        try:
            os.system('rename _checkpoint _rst *_checkpoint')
        except Exception:
            self.logger.abort('Renaming failed, see if checkpoint files exists')

    def execute(self):

        self.logger.info('Obtaining GEOS restarts for the coupled simulation')

        # Create config get object for script brevity
        # -------------------------------------------
        scg=self.config_get

        # Obtain current and previous cycle time objects
        # ----------------------------------------------
        current_cycle = scg('current_cycle')
        cc_dto = dt.strptime(current_cycle, "%Y%m%dT%H%M%SZ")

        start_cycle_point = scg('start_cycle_point')
        sc_dto = dt.strptime(start_cycle_point, "%Y-%m-%dT%H:%M:%SZ")

        self.cycle_dir = scg('cycle_dir')
        self.swell_static_files = scg('swell_static_files')

        # Previous cycle folder name
        # ----------------------------------
        self.forecast_duration = scg('forecast_duration')
        self.previous_cycle_dir = self.previous_cycle(self.cycle_dir, self.forecast_duration)

        # Create an empty restart directory
        # ----------------------------------
        os.mkdir(os.path.join(self.cycle_dir, 'RESTART'))

        # Restarts should be provided
        # --------------------------------------------------
        if sc_dto == cc_dto:
            self.initial_restarts()
        else:
            self.cycling_restarts()
            self.rename_checkpoints()

# --------------------------------------------------------------------------------------------------
