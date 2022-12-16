# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# -----------------------------------------------
import os
import shutil

from swell.tasks.base.task_base import taskBase
# from swell.utilities.filehandler import *
# from swell.utilities.exceptions import *

# --------------------------------------------------------------------------------------------------

class GenerateBClimatology(taskBase):

    def execute(self):
        """Acquires B Matrix files 

            TODO: Generate Bump files for any np if not created already

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """

        total_processors = self.config_get('total_processors')
        swell_static_files = self.config_get('swell_static_files')
        horizontal_resolution = self.config_get('horizontal_resolution')
        vertical_resolution = self.config_get('vertical_resolution')
        background_error_model = self.config_get('background_error_model')
        cycle_dir = self.config_get('cycle_dir')

        if background_error_model == 'bump':
            # Folder name contains both horizontal and vertical resolutions 
            # ----------------------------
            resolution = horizontal_resolution + 'x' + vertical_resolution

            # Compute number of processors
            # ----------------------------
            np_string = self.use_config_to_template_string(total_processors)
            np = eval(np_string)
            
            # Get the name of the model component
            # --------------------------------
            model_component = self.get_model()

            # jedi_interface = self.config_get('jedi_interface')

            # Load experiment file
            # --------------------
            b_dir = os.path.join(swell_static_files, 'jedi', 'soca', model_component, 
                        background_error_model,'climatological',resolution,str(np))
            
            self.logger.info('  Copying BUMP files from: '+b_dir)
            shutil.copytree(b_dir, '/discover/nobackup/dardag/scratch/',
                        dirs_exist_ok=True)         
        else:
            self.logger.abort('  Background error model is not ready')

        exit()
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


# --------------------------------------------------------------------------------------------------
