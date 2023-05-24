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
        window_type = self.config.window_type()
        window_offset = self.config.window_offset()
        background_time_offset = self.config.background_time_offset()
        number_of_iterations = self.config.number_of_iterations()
        observations = self.config.observations()

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
        self.jedi_rendering.add_key('window_length', self.config.window_length())
        self.jedi_rendering.add_key('minimizer', self.config.minimizer())
        self.jedi_rendering.add_key('number_of_iterations', number_of_iterations[0])
        self.jedi_rendering.add_key('analysis_variables', self.config.analysis_variables())
        self.jedi_rendering.add_key('gradient_norm_reduction',
                                    self.config.gradient_norm_reduction())

        # Background
        self.jedi_rendering.add_key('horizontal_resolution', self.config.horizontal_resolution())
        self.jedi_rendering.add_key('local_background_time', local_background_time)
        self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)

        # Geometry
        self.jedi_rendering.add_key('npx_proc', self.config.npx_proc(None))
        self.jedi_rendering.add_key('npy_proc', self.config.npy_proc(None))
        self.jedi_rendering.add_key('total_processors', self.config.total_processors(None))
        self.jedi_rendering.add_key('vertical_resolution', self.config.vertical_resolution())

        # Observations
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', self.config.crtm_coeff_dir(None))
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
        jedi_dictionary_iterator(jedi_config_dict, self.jedi_rendering, window_type, observations,
                                 self.config.jedi_forecast_model(None))


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
        np = eval(model_component_meta['total_processors'])

        # Run the JEDI executable
        # -----------------------
        run_executable(self.logger, self.cycle_dir(), np, jedi_executable_path, jedi_config_file,
                       output_log_file)
        self.logger.info('Running '+jedi_executable_path+' with '+str(np)+' processors.')


# --------------------------------------------------------------------------------------------------
