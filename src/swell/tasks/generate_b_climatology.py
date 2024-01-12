# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# -----------------------------------------------
import os
import numpy as np
import netCDF4 as nc
from scipy.ndimage import gaussian_filter, distance_transform_edt
import yaml

from swell.tasks.base.task_base import taskBase
from swell.utilities.shell_commands import run_subprocess, run_track_log_subprocess
from swell.utilities.run_jedi_executables import jedi_dictionary_iterator

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
                    value_dict = self.jedi_rendering.render_interface_model(value_file)
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

            self.logger.abort('  BUMP method is not actively supported.')
            return self.generate_bump()

        elif self.background_error_model == 'explicit_diffusion':

            return self.generate_explicit_diffusion()
        else:
            self.logger.abort('  Unknown background error model')

    # ----------------------------------------------------------------------------------------------

    def generate_bump(self):

        self.logger.info(' Generating BUMP files.')

        # Jedi configuration file
        # -----------------------
        jedi_config_file = os.path.join(self.cycle_dir(), 'jedi_bump_config.yaml')

        # Generate the JEDI configuration file for running the executable
        # ---------------------------------------------------------------
        jedi_config_dict = self.generate_jedi_config()

        with open(jedi_config_file, 'w') as jedi_config_file_open:
            yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

        # Get the JEDI interface metadata
        # -------------------------------
        model_component_meta = self.jedi_rendering.render_interface_meta()

        # Jedi executable name
        # --------------------
        jedi_executable = model_component_meta['executables']['bump']
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

    def generate_explicit_diffusion(self):

        self.logger.info(' Generating vertical correlation files.')
        self.obtain_scales()

    # ----------------------------------------------------------------------------------------------

    def obtain_scales(self):

        # This is the copy of calc_scales.py under SOCA/tools to obtain the vertical scale.
        # The output then will be used to generate the vertical correlation files via
        # parameters_diffusion_vt

        # Jedi application name
        # ---------------------
        jedi_application = 'calc_scales'

        # Open the JEDI config file and fill initial templates
        # ----------------------------------------------------
        jedi_config_dict = self.jedi_rendering.render_oops_file(f'{jedi_application}')

        # Jedi configuration file
        # -----------------------
        jedi_config_file = os.path.join(self.cycle_dir(), f'{jedi_application}.yaml')

        # Write the expanded dictionary to YAML file
        # ------------------------------------------
        with open(jedi_config_file, 'w') as jedi_config_file_open:
            yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

        mod_file = os.path.join(self.experiment_path(), 'jedi_bundle', 'build', 'modules')

        # Source JEDI modules and execute calc_scales.py
        # Could be a generalized function depending on the repeated use of this
        # -----------------------------------------------------------------------
        command = f'source {mod_file} \n' + \
            f'cd {self.cycle_dir()} \n' + \
            f'{self.cycle_dir()}/soca/calc_scales.py {self.cycle_dir()}/calc_scales.yaml'

        # Containerized run of the script
        # -------------------------------
        run_subprocess(self.logger, ['/bin/bash', '-c', command])

    # ----------------------------------------------------------------------------------------------

    def execute(self):
        """ Creates B Matrix files for background error model(s):

            - BUMP:
             Creates bump files in 'cycle_dir' that depend upon the number of total
             processors and active model components (sea-ice or no sea-ice).

            - EXPLICIT_DIFFUSION:
             Uses the methodology described in Weaver et al. (20xx). This requires
             creating horizontal (offline) and vertical diffusion (online with irregular
             frequency) parameter files. With SOCA, implementation, it is also required
             to have horizontal length scales defined beforehand.

        Parameters
        ----------
            All inputs are extracted from the JEDI experiment file configuration.
            See the taskBase constructor for more information.
        """

        # Parse configuration
        # -------------------
        window_offset = self.config.window_offset()
        window_type = self.config.window_type()
        background_error_model = self.config.background_error_model()
        self.swell_static_files = self.config.swell_static_files()
        self.horizontal_resolution = self.config.horizontal_resolution()
        self.vertical_resolution = self.config.vertical_resolution()

        # Get the JEDI interface for this model component
        # -----------------------------------------------
        self.jedi_rendering.add_key('npx_proc', self.config.npx_proc(None))
        self.jedi_rendering.add_key('npy_proc', self.config.npy_proc(None))
        self.jedi_rendering.add_key('total_processors', self.config.total_processors(None))
        self.jedi_rendering.add_key('analysis_variables', self.config.analysis_variables())
        self.jedi_rendering.add_key('background_error_model', self.config.background_error_model())

        # Compute data assimilation window parameters
        # -------------------------------------------
        self.local_background_time = self.da_window_params.local_background_time(window_offset,
                                                                            window_type)

        # Background
        # ----------
        self.jedi_rendering.add_key('local_background_time', self.local_background_time)

        model_component_meta = self.jedi_rendering.render_interface_meta()
        self.jedi_interface = model_component_meta['jedi_interface']

        # Compute number of processors
        # ----------------------------
        self.np = eval(str(model_component_meta['total_processors']))

        # Obtain and initialize proper error model
        # ----------------------------------------
        self.background_error_model = background_error_model
        self.initialize_background()

# --------------------------------------------------------------------------------------------------
