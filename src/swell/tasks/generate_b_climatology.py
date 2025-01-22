# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# -----------------------------------------------
import os
import yaml

from swell.tasks.base.task_base import taskBase
from swell.utilities.shell_commands import run_track_log_subprocess
from swell.utilities.run_jedi_executables import jedi_dictionary_iterator
from swell.utilities.file_system_operations import check_if_files_exist_in_path

# --------------------------------------------------------------------------------------------------


class GenerateBClimatology(taskBase):

    def jedi_dictionary_iterator(self, jedi_config_dict: dict) -> None:

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

    def generate_jedi_config(self) -> dict:

        # Render StaticBInit (no templates needed)
        # ----------------------------------------
        jedi_config_dict = self.jedi_rendering.render_oops_file('StaticBInit')

        # Read configs for the rest of the dictionary
        # -------------------------------------------
        self.jedi_dictionary_iterator(jedi_config_dict)

        return jedi_config_dict

    # ----------------------------------------------------------------------------------------------

    def initialize_background(self) -> None:

        if self.background_error_model == 'bump':

            self.logger.abort('  BUMP method is not currently supported.')
            self.generate_bump()

        elif self.background_error_model == 'explicit_diffusion':

            self.generate_explicit_diffusion()
        else:
            self.logger.abort('  Unknown background error model')

    # ----------------------------------------------------------------------------------------------

    def generate_bump(self) -> None:

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

    # ----------------------------------------------------------------------------------------------

    def generate_explicit_diffusion(self) -> None:
        # This will use static horizontal correlation files and generate the vertical correlation
        # file based on the MLD.

        self.logger.info(' Generating files required by EXPLICIT_DIFFUSION.')
        self.obtain_scales()
        self.parameters_diffusion_vt()

    # ----------------------------------------------------------------------------------------------

    def obtain_scales(self) -> None:

        # This executes calc_scales.py under SOCA/tools to obtain the vertical scale.
        # The output then will be used to generate the vertical correlation files via
        # parameters_diffusion_vt
        # ----------------------------------------------------------------------------
        self.logger.info(' Creating the horizontal and vertical correlation scales.')

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

        # Execute calc_scales.py, which is a Python script in SOCA/tools
        # Make sure the file is executable
        # -----------------------------------------------------------------------
        exec_file = os.path.join(self.cycle_dir(), 'soca', 'calc_scales.py')
        os.chmod(exec_file, 0o755)

        # Create and execute the command
        # ------------------------------
        command = [exec_file, 'calc_scales.yaml']
        run_track_log_subprocess(self.logger, command, cwd=self.cycle_dir())

    # ----------------------------------------------------------------------------------------------

    def parameters_diffusion_vt(self) -> None:

        # This generates the MLD dependent vertical correlation file using the
        # calculated_scales
        # ---------------------------------------------------------------------
        self.logger.info(' Creating the MLD dependent vertical corr. file')

        # Jedi application name
        # ---------------------
        jedi_application = 'parameters_diffusion_vt'

        # Open the JEDI config file and fill initial templates
        # ----------------------------------------------------
        jedi_config_dict = self.jedi_rendering.render_oops_file(f'{jedi_application}')

        # Jedi configuration file
        # -----------------------
        jedi_config_file = os.path.join(self.cycle_dir(), f'jedi_{jedi_application}_config.yaml')

        # Output log file
        # ---------------
        output_log_file = os.path.join(self.cycle_dir(), f'jedi_{jedi_application}_log.log')

        # Perform complete template rendering
        # -----------------------------------
        jedi_dictionary_iterator(jedi_config_dict, self.jedi_rendering)

        with open(jedi_config_file, 'w') as jedi_config_file_open:
            yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

        # Get the JEDI interface metadata
        # -------------------------------
        model_component_meta = self.jedi_rendering.render_interface_meta()

        # Jedi executable name
        # --------------------
        jedi_executable = model_component_meta['executables']['explicit_diffusion']
        jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle',
                                            'build', 'bin', jedi_executable)

        # Run the JEDI executable
        # -----------------------
        if not self.generate_yaml_and_exit:
            self.logger.info('Running '+jedi_executable_path+' with '+str(self.np)+' processors.')
            command = ['mpirun', '-np', str(self.np), jedi_executable_path, jedi_config_file]

            # Move to the cycle directory
            # ---------------------------
            background_error_model_dir = os.path.join(self.cycle_dir(), 'background_error_model')
            if not os.path.exists(background_error_model_dir):
                os.mkdir(background_error_model_dir)

            # Execute
            # -------
            run_track_log_subprocess(self.logger, command, output_log_file, cwd=self.cycle_dir())

        else:
            self.logger.info('YAML generated, now exiting.')

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:
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

        swell_static_files_user = self.config.swell_static_files_user(None)
        self.swell_static_files = self.config.swell_static_files()

        # Use static_files_user if present in config and contains files
        # -------------------------------------------------------------
        if swell_static_files_user is not None:
            self.logger.info('swell_static_files_user specified, checking for files')
            if check_if_files_exist_in_path(self.logger, swell_static_files_user):
                self.logger.info(f'Using swell static files in {swell_static_files_user}')
                self.swell_static_files = swell_static_files_user

        self.horizontal_resolution = self.config.horizontal_resolution()
        self.vertical_resolution = self.config.vertical_resolution()
        self.generate_yaml_and_exit = self.config.generate_yaml_and_exit(False)

        # Get the JEDI interface for this model component
        # -----------------------------------------------
        self.jedi_rendering.add_key('npx_proc', self.config.npx_proc(None))
        self.jedi_rendering.add_key('npy_proc', self.config.npy_proc(None))
        self.jedi_rendering.add_key('total_processors', self.config.total_processors(None))
        self.jedi_rendering.add_key('analysis_variables', self.config.analysis_variables())
        self.jedi_rendering.add_key('background_error_model', self.config.background_error_model())
        self.jedi_rendering.add_key('marine_models', self.config.marine_models(None))
        # Compute data assimilation window parameters
        # -------------------------------------------
        local_background_time = self.da_window_params.local_background_time(window_offset,
                                                                            window_type)
        local_background_time_iso = self.da_window_params.local_background_time_iso(window_offset,
                                                                                    window_type)

        # Background
        # ----------
        self.jedi_rendering.add_key('local_background_time', local_background_time)
        self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)

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
