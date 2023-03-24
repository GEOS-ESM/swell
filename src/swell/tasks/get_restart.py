# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import shutil
import os
import glob

from swell.tasks.base.task_base import taskBase
# from swell.tasks.prep_geos_run_dir import *
from datetime import datetime as dt

# --------------------------------------------------------------------------------------------------


class GetRestart(taskBase):

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
            dst_dir = self.cycle_dir

        # Fetch more resolution dependent files
        # -------------------------------------
        

    def cycling_restarts(self):
        self.logger.info('GEOS restarts will be taken from the previous cycle')

    def rename_checkpoints(self):
        self.logger.info('Renaming *_checkpoint files to *_rst')

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

        # Restarts should be provided
        # ---------------------------------------
        if sc_dto == cc_dto:
            self.initial_restarts()
        else:
            self.cycling_restarts()



# --------------------------------------------------------------------------------------------------
