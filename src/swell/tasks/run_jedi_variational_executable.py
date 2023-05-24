# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.tasks.base.task_base import taskBase
from swell.utilities.run_jedi_executables import jedi_dictionary_iterator, run_executable


# --------------------------------------------------------------------------------------------------


class RunJediVariationalExecutable(taskBase):

    def execute(self):

        # Parse configuration
        # -------------------
        window_type = self.config_get('window_type')
        npx_proc = self.config_get('npx_proc', None)
        npy_proc = self.config_get('npy_proc', None)
        total_processors = self.config_get('total_processors', None)
        window_length = self.config_get('window_length')
        horizontal_resolution = self.config_get('horizontal_resolution')
        vertical_resolution = self.config_get('vertical_resolution')
        crtm_coeff_dir = self.config_get('crtm_coeff_dir', None)
        window_offset = self.config_get('window_offset')
        background_time_offset = self.config_get('background_time_offset')
        number_of_iterations = self.config_get('number_of_iterations')
        minimizer = self.config_get('minimizer')
        analysis_variables = self.config_get('analysis_variables')
        gradient_norm_reduction = self.config_get('gradient_norm_reduction')
        observations = self.config_get('observations')

        # Compute data assimilation window parameters
        background_time = self.da_window_params.background_time(window_offset,
                                                                background_time_offset)
        local_background_time = self.da_window_params.local_background_time(window_offset,
                                                                            window_type)
        local_background_time_iso = self.da_window_params.local_background_time_iso(window_offset,
                                                                                    window_type)
        window_begin = self.da_window_params.window_begin(window_offset)
        window_begin_iso = self.da_window_params.window_begin_iso(window_offset)

        # Populate jedi interface templates dictionary
        # --------------------------------------------
        self.jedi_rendering.add_key('window_begin_iso', window_begin_iso)
        self.jedi_rendering.add_key('window_length', window_length)
        self.jedi_rendering.add_key('minimizer', minimizer)
        self.jedi_rendering.add_key('number_of_iterations', number_of_iterations[0])
        self.jedi_rendering.add_key('analysis_variables', analysis_variables)
        self.jedi_rendering.add_key('gradient_norm_reduction', gradient_norm_reduction)

        # Background
        self.jedi_rendering.add_key('horizontal_resolution', horizontal_resolution)
        self.jedi_rendering.add_key('local_background_time', local_background_time)
        self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)

        # Geometry
        self.jedi_rendering.add_key('npx_proc', npx_proc)
        self.jedi_rendering.add_key('npy_proc', npy_proc)
        self.jedi_rendering.add_key('vertical_resolution', vertical_resolution)

        # Observations
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', crtm_coeff_dir)
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Jedi configuration file
        # -----------------------
        jedi_config_file = os.path.join(self.cycle_dir(), 'jedi_variational_config.yaml')

        # Output log file
        # ---------------
        output_log_file = os.path.join(self.cycle_dir(), 'jedi_variational_log.log')

        # Get the JEDI interface for this model component
        # -----------------------------------------------
        model_component_meta = self.jedi_rendering.render_interface_meta()
        jedi_interface = model_component_meta['jedi_interface']

        # Generate the JEDI configuration file for running the executable
        # ---------------------------------------------------------------
        jedi_config_dict = self.jedi_rendering.render_oops_file(f'variational{window_type}')

        # Perform complete template rendering
        # -----------------------------------
        jedi_dictionary_iterator(jedi_config_dict, window_type)

        # Write the expanded dictionary to YAML file
        # ------------------------------------------
        with open(jedi_config_file, 'w') as jedi_config_file_open:
            yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

        # Jedi executable name
        # --------------------
        jedi_executable = model_component_meta['executables'][f'variational{window_type}']
        jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle', 'build',
                                            'bin', jedi_executable)
        # Compute number of processors
        # ----------------------------
        total_processors = total_processors.replace('npx_proc', str(npx_proc))
        total_processors = total_processors.replace('npy_proc', str(npy_proc))
        np = eval(total_processors)

        # Run the JEDI executable
        # -----------------------
        run_executable(self.cycle_dir(), np, jedi_executable_path, jedi_config_file,
                            output_log_file)
        self.logger.info('Running '+jedi_executable_path+' with '+str(np)+' processors.')


# --------------------------------------------------------------------------------------------------
