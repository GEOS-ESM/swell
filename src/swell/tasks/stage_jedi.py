# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from swell.swell_path import get_swell_path
from swell.configuration.question_defaults import *
from swell.tasks.base.task_base import taskBase
from swell.utilities.filehandler import get_file_handler
from swell.utilities.exceptions import SwellError
from swell.utilities.file_system_operations import check_if_files_exist_in_path


# --------------------------------------------------------------------------------------------------


class StageJedi(taskBase):

    def execute(self) -> None:
        """Acquires listed files under the configuration/jedi/interface/model/stage.yaml file.

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """

        # Extract potential template variables from config
        horizontal_resolution = self.config.resolve(horizontal_resolution)

        swell_static_files_user = self.config.resolve(swell_static_files_user, default=None)
        swell_static_files = self.config.resolve(swell_static_files)

        # Use static_files_user if present in config and contains files
        # -------------------------------------------------------------
        if swell_static_files_user is not None and swell_static_files_user != 'None':
            self.logger.info('swell_static_files_user specified, checking for files')
            if check_if_files_exist_in_path(self.logger, swell_static_files_user):
                self.logger.info(f'Using swell static files in {swell_static_files_user}')
                swell_static_files = swell_static_files_user

        vertical_resolution = self.config.resolve(vertical_resolution)
        npx_proc = self.config.resolve(npx_proc, default=None)
        npy_proc = self.config.resolve(npy_proc, default=None)
        gsibec_configuration = self.config.resolve(gsibec_configuration, default=None)
        gsibec_nlats = self.config.resolve(gsibec_nlats, default=None)
        gsibec_nlons = self.config.resolve(gsibec_nlons, default=None)
        saber_central_block = self.config.resolve(saber_central_block, default=None)

        # Add jedi interface template keys
        self.jedi_rendering.add_key('horizontal_resolution', horizontal_resolution)
        self.jedi_rendering.add_key('swell_static_files', swell_static_files)
        self.jedi_rendering.add_key('vertical_resolution', vertical_resolution)
        self.jedi_rendering.add_key('npx_proc', npx_proc)
        self.jedi_rendering.add_key('npy_proc', npy_proc)
        self.jedi_rendering.add_key('gsibec_configuration', gsibec_configuration)
        self.jedi_rendering.add_key('gsibec_nlats', gsibec_nlats)
        self.jedi_rendering.add_key('gsibec_nlons', gsibec_nlons)
        self.jedi_rendering.add_key('saber_central_block', saber_central_block)

        # Open the stage configuration file
        # ---------------------------------
        stage_file = 'stage'
        if self.is_datetime_dependent():
            stage_file = 'stage_cycle'

        # Check for presence of stage file
        # --------------------------------
        stage_pathfile = os.path.join(get_swell_path(), 'configuration', 'jedi', 'interfaces',
                                      self.get_model(), 'model', stage_file + '.py')

        if not os.path.exists(stage_pathfile):
            self.logger.info('No stage dictionary was found for this configuration')
            return

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
        except SwellError as e:
            self.logger.abort(str(e))
