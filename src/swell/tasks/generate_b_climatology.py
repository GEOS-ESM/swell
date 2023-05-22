# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# -----------------------------------------------
import os
import shutil

import yaml

from swell.tasks.base.task_base import taskBase
from swell.utilities.shell_commands import run_track_log_subprocess
from swell.utilities.render_jedi_interface_files import template_dictionary_oops_config, \
                                                        read_render_jedi_interface_oops,

# --------------------------------------------------------------------------------------------------


interface_executable = {
  'soca': 'soca_staticbinit.x',
}

# --------------------------------------------------------------------------------------------------


class GenerateBClimatology(taskBase):

    def jedi_dictionary_iterator(self, jedi_config_dict):

        # Loop over dictionary and replace if value is a dictionary
        # ---------------------------------------------------------
        for key, value in jedi_config_dict.items():
            if isinstance(value, dict):
                self.jedi_dictionary_iterator(value)
            else:
                if 'TASKFILL' in value:
                    value_file = value.replace('TASKFILL', '')
                    value_dict = self.open_jedi_interface_model_config_file(value_file)
                    jedi_config_dict[key] = value_dict

    # ----------------------------------------------------------------------------------------------

    def generate_jedi_config(self):

        # Render StaticBInit (no templates needed)
        # ----------------------------------------
        jedi_config_dict = self.jedi_rendering.render_oops_file('StaticBInit')

        # Read configs for the rest of the dictionary
        # -------------------------------------------
        self.jedi_dictionary_iterator(jedi_config_dict)

        return jedi_config_dict

    # ----------------------------------------------------------------------------------------------

    def initialize_background(self):

        if self.background_error_model == 'bump':

            return self.generate_bump()
        else:
            self.logger.abort('  Unknown background error model')

    def generate_bump(self):

        # Folder name contains both horizontal and vertical resolutions
        # ----------------------------
        resolution = self.horizontal_resolution + 'x' + self.vertical_resolution

        # Get the name of the model component
        # --------------------------------
        model_component = self.get_model()

        # Load experiment file
        # --------------------
        b_dir = os.path.join(self.swell_static_files, 'jedi', self.jedi_interface,
                             model_component, self.background_error_model, 'climatological',
                             resolution, str(self.np))

        d_dir = os.path.join(self.cycle_dir(), 'background_error_model')

        try:
            self.logger.info('  Copying BUMP files from: '+b_dir)
            shutil.copytree(b_dir, d_dir, dirs_exist_ok=True)

        except Exception:
            self.logger.info('  Copying failed, generating BUMP files.')

            # Jedi configuration file
            # -----------------------
            jedi_config_file = os.path.join(self.cycle_dir(), 'jedi_bump_config.yaml')

            # Generate the JEDI configuration file for running the executable
            # ---------------------------------------------------------------
            jedi_config_dict = self.generate_jedi_config()

            with open(jedi_config_file, 'w') as jedi_config_file_open:
                yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

            # Jedi executable name
            # --------------------
            jedi_executable = interface_executable[self.jedi_interface]
            jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle',
                                                'build', 'bin', jedi_executable)

            # Run the JEDI executable
            # -----------------------
            self.logger.info('Running '+jedi_executable_path+' with '+str(self.np)+' processors.')

            command = ['mpirun', '-np', str(self.np), jedi_executable_path, jedi_config_file]

            # Move to the cycle directory
            # ---------------------------
            os.chdir(self.cycle_dir())
            if not os.path.exists('background_error_model'):
                os.mkdir('background_error_model')

            # Execute
            # -------
            run_track_log_subprocess(self.logger, command)

        return

    # ----------------------------------------------------------------------------------------------

    def execute(self):
        """Acquires B Matrix files for background error model(s):

            - Bump:
            Tries fetching existing bump files (contingent upon the number of
            total processors), creates new ones in 'cycle_dir' otherwise.

            - TODO GSI:

        Parameters
        ----------
            All inputs are extracted from the JEDI experiment file configuration.
            See the taskBase constructor for more information.
        """

        self.total_processors = self.config_get('total_processors')
        self.swell_static_files = self.config_get('swell_static_files')
        self.horizontal_resolution = self.config_get('horizontal_resolution')
        self.vertical_resolution = self.config_get('vertical_resolution')
        self.npx_proc = self.config_get('npx_proc')  # Used in eval(total_processors)
        self.npy_proc = self.config_get('npy_proc')  # Used in eval(total_processors)

        # Get the JEDI interface for this model component
        # -----------------------------------------------
        model_component_meta = self.jedi_rendering.render_interface_meta()
        self.jedi_interface = model_component_meta['jedi_interface']

        # Compute number of processors
        # ----------------------------
        self.total_processors = self.total_processors.replace('npx_proc', str(self.npx_proc))
        self.total_processors = self.total_processors.replace('npy_proc', str(self.npy_proc))
        self.np = eval(self.total_processors)

        # Obtain and initialize proper error model
        # -----------------------------------------------
        self.background_error_model = self.config_get('background_error_model')
        self.initialize_background()

# --------------------------------------------------------------------------------------------------
