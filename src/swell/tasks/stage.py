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


class Stage(taskBase):

    def execute(self):
        """Acquires listed files under the YAML STAGE directive.

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """

        print(self.__config__.__config__)

        return

        # Name of JEDI interfaces
        jedi_interface = self.config_get_model('jedi_interface')
        jedi_interface_swell = self.config_get_model('jedi_interface_swell')

        # Get stage configuration
        swell_exp_config_path = self.get_swell_exp_config_path()

        # Jedi stage configuration file
        jedi_stage_config = os.path.join(swell_exp_config_path, 'jedi', jedi_interface,
                                         jedi_interface_swell, 'model', 'stage.yaml')

        # Open stage config file
        stage_config = self.open_config_file(jedi)

        try:
            fh = get_file_handler(stage_config)
            if not fh.is_ready():
                self.logger.abort('One or more files not ready')
            else:
                fh.get()
        except SWELLError as e:
            self.logger.abort(str(e))
