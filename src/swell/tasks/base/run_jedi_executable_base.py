# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from abc import ABC, abstractmethod
import os

from swell.tasks.base.task_base import taskBase
from swell.utilities.shell_commands import run_track_log_subprocess


# --------------------------------------------------------------------------------------------------


class RunJediExecutableBase(taskBase):

    # ----------------------------------------------------------------------------------------------

    @abstractmethod
    def execute(self):
        # This class does not execute, it provides helper function for the children
        # ------------------------------------------------------------------------
        pass

    # ----------------------------------------------------------------------------------------------

    def jedi_dictionary_iterator(self, jedi_config_dict, window_type):

        # Assemble configuration YAML file
        # --------------------------------
        for key, value in jedi_config_dict.items():
            if isinstance(value, dict):
                self.jedi_dictionary_iterator(value, window_type)

            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self.jedi_dictionary_iterator(item, window_type)

            else:
                if 'TASKFILL' in value:
                    value_file = value.replace('TASKFILL', '')
                    value_dict = self.jedi_rendering.render_interface_model(value_file)

                    jedi_config_dict[key] = value_dict

                elif 'SPECIAL' in value:
                    value_special = value.replace('SPECIAL', '')
                    if value_special == 'observations':
                        observations = []
                        obs = self.config_get('observations')
                        for ob in obs:
                            # Get observation dictionary
                            obs_dict = self.jedi_rendering.render_interface_observations(ob)
                            observations.append(obs_dict)
                        jedi_config_dict[key] = observations

                    elif value_special == 'model' and window_type == '4D':
                        model = self.config_get('model')
                        model_dict = self.jedi_rendering.render_interface_model(model)
                        jedi_config_dict[key] = model_dict

    # ----------------------------------------------------------------------------------------------

    def generate_jedi_config(self, jedi_application, window_type):

        # Var suite names are handled in variational executable
        # -----------------------------------------------------
        if 'var' not in jedi_application:
            jedi_application = jedi_application + window_type

        # Build dictionary for rendering JEDI configuration files
        analysis_variables = self.config_get('analysis_variables', None)
        gradient_norm_reduction = self.config_get('gradient_norm_reduction', None)
        minimizer = self.config_get('minimizer', None)
        number_of_iterations = self.config_get('number_of_iterations', None)
        window_length = self.config_get('window_length', None)
        background_frequency = self.config_get('background_frequency', None)
        horizontal_resolution = self.config_get('horizontal_resolution', None)
        npx_proc = self.config_get('npx_proc', None)
        npy_proc = self.config_get('npy_proc', None)
        swell_static_files = self.config_get('swell_static_files', None)
        vertical_resolution = self.config_get('vertical_resolution', None)
        crtm_coeff_dir = self.config_get('crtm_coeff_dir', None)
        window_offset = self.config_get('window_offset', None)
        background_time_offset = self.config_get('background_time_offset', None)

        # Compute data assimilation window parameters
        background_time = self.da_window_params.background_time(window_offset,
                                                                background_time_offset)
        local_background_time = self.da_window_params.local_background_time(window_offset,
                                                                            window_type)
        local_background_time_iso = self.da_window_params.local_background_time_iso(window_offset,
                                                                                    window_type)
        window_begin = self.da_window_params.window_begin(window_offset)
        window_begin_iso = self.da_window_params.window_begin_iso(window_offset)

        # Add config to template rendering dictionary
        self.jedi_rendering.add_key('analysis_variables', analysis_variables)
        self.jedi_rendering.add_key('gradient_norm_reduction', gradient_norm_reduction)
        self.jedi_rendering.add_key('minimizer', minimizer)
        self.jedi_rendering.add_key('number_of_iterations', number_of_iterations)
        self.jedi_rendering.add_key('window_begin_iso', window_begin_iso)
        self.jedi_rendering.add_key('window_length', window_length)
        self.jedi_rendering.add_key('background_frequency', background_frequency)
        self.jedi_rendering.add_key('horizontal_resolution', horizontal_resolution)
        self.jedi_rendering.add_key('local_background_time', local_background_time)
        self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)
        self.jedi_rendering.add_key('npx_proc', npx_proc)
        self.jedi_rendering.add_key('npy_proc', npy_proc)
        self.jedi_rendering.add_key('swell_static_files', swell_static_files)
        self.jedi_rendering.add_key('vertical_resolution', vertical_resolution)
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', crtm_coeff_dir)
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Create dictionary from the templated JEDI config file
        # -----------------------------------------------------
        jedi_config_dict = self.jedi_rendering.render_oops_file(jedi_application)

        # Read configs for the rest of the dictionary
        # -------------------------------------------
        self.jedi_dictionary_iterator(jedi_config_dict, window_type)

        return jedi_config_dict

    # ----------------------------------------------------------------------------------------------

    def run_executable(self, cycle_dir, np, jedi_executable_path, jedi_config_file, output_log):

        # Run the JEDI executable
        # -----------------------
        self.logger.info('Running '+jedi_executable_path+' with '+str(np)+' processors.')

        command = ['mpirun', '-np', str(np), jedi_executable_path, jedi_config_file]

        # Move to the cycle directory
        # ---------------------------
        os.chdir(cycle_dir)

        # Run command
        # -----------
        run_track_log_subprocess(self.logger, command, output_log=output_log)


# --------------------------------------------------------------------------------------------------
