# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import re
import glob
from shutil import copyfile

from swell.tasks.base.task_base import taskBase
from swell.utilities.filehandler import *
from swell.utilities.exceptions import *
from r2d2 import fetch


# --------------------------------------------------------------------------------------------------


class StageJedi(taskBase):

    def execute(self):
        """Acquires listed files under the configuration/jedi/interface/model/stage.yaml file.

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """

        # Extract potential template variables from config
        horizontal_resolution = self.config_get('horizontal_resolution')
        swell_static_files = self.config_get('swell_static_files')
        vertical_resolution = self.config_get('vertical_resolution')

        # Add jedi interface template keys
        self.jedi_rendering.add_key('horizontal_resolution', horizontal_resolution)
        self.jedi_rendering.add_key('swell_static_files', swell_static_files)
        self.jedi_rendering.add_key('vertical_resolution', vertical_resolution)

        # Open the stage configuration file
        # ---------------------------------
        stage_file = 'stage'
        if self.is_datetime_dependent():
            stage_file = 'stage_cycle'

        # Check for presence of stage file
        # --------------------------------
        stage_pathfile = os.path.join(self.experiment_config_path(), 'jedi', 'interfaces',
                                      self.get_model(), 'model', stage_file + '.yaml')
        print(stage_file)
        if not os.path.exists(stage_pathfile):
            self.logger.info('No stage dictionary was found for this configuration')
            exit(0)

        # Open file and template it
        stage_dict = self.jedi_rendering.render_interface_model(stage_file)

        # Run the file handler
        # --------------------
        try:
            fh = get_file_handler(stage_dict)
            if not fh.is_ready():
                self.logger.abort('One or more files not ready')
            else:
                fh.get()
        except SWELLError as e:
            self.logger.abort(str(e))
