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

        # Open the stage configuration file
        # ---------------------------------
        stage_file = 'stage'
        if self.is_datetime_dependent():
            stage_file = 'stage_cycle'

        stage_dict = self.open_jedi_interface_model_config_file(stage_file)

        # Check that the passed configuration had a stage component
        if stage_dict is None:
            self.logger.info('No stage dictionary was found for this configuration')
            exit(0)

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
