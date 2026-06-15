# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
from ruamel.yaml import YAML

from swell.tasks.base.task_base import taskBase
from swell.tasks.base.task_setup import TaskSetup
from swell.tasks.base.task_attributes import task_attributes
import swell.configuration.question_defaults as qd
from swell.utilities.run_jedi_executables import run_executable


# --------------------------------------------------------------------------------------------------

task_name = 'RunJediFgatExecutable'


@task_attributes.register(task_name)
class Setup(TaskSetup):
    def set_defaults(self):
        self.base_name = task_name
        self.is_cycling = True
        self.model_dep = True
        self.task_time_limit = True
        self.slurm = {}
        self.questions = [
            qd.background_time_offset(),
            qd.crtm_coeff_dir(),
            qd.observations(),
            qd.observing_system_records_path(),
            qd.npx_proc(),
            qd.npy_proc(),
            qd.npx(),
            qd.npy(),
            qd.horizontal_resolution(),
            qd.vertical_resolution(),
            qd.window_length(),
            qd.window_type(),
            qd.analysis_variables(),
            qd.background_frequency(),
            qd.generate_yaml_and_exit(),
            qd.gradient_norm_reduction(),
            qd.gsibec_configuration(),
            qd.jedi_forecast_model(),
            qd.minimizer(),
            qd.gsibec_nlats(),
            qd.gsibec_nlons(),
            qd.number_of_iterations(),
            qd.total_processors(),
            qd.marine_models(),
            qd.comparison_log_type('fgat'),
            qd.mock_experiment()
        ]

# --------------------------------------------------------------------------------------------------


class RunJediFgatExecutable(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        # Jedi application name
        # ---------------------
        jedi_application = 'fgat'

        # Parse configuration
        # -------------------
        marine_models = self.config.marine_models()
        window_type = self.config.window_type()
        window_length = self.config.window_length()
        background_time_offset = self.config.background_time_offset()
        number_of_iterations = self.config.number_of_iterations()
        jedi_forecast_model = self.config.jedi_forecast_model(None)
        generate_yaml_and_exit = self.config.generate_yaml_and_exit(False)

        # Atmosphere specific settings
        # ----------------------------
        # Set the observing system records path
        self.jedi_rendering.set_obs_records_path(self.config.observing_system_records_path(None))

        gsibec_nlats = self.config.gsibec_nlats(None)
        gsibec_nlons = self.config.gsibec_nlons(None)
        npx_proc = self.config.npx_proc(None)
        npy_proc = self.config.npy_proc(None)

        # Compute data assimilation window parameters
        # --------------------------------------------
        background_time = self.da_window_params.background_time(background_time_offset)
        local_background_time = self.da_window_params.local_background_time(window_length,
                                                                            window_type)
        local_background_time_iso = self.da_window_params.local_background_time_iso(window_length,
                                                                                    window_type)
        window_begin = self.da_window_params.window_begin(window_length)
        window_begin_iso = self.da_window_params.window_begin_iso(window_length)
        window_end_iso = self.da_window_params.window_end_iso(window_length)

        # Populate jedi interface templates dictionary
        # --------------------------------------------
        self.jedi_rendering.add_key('marine_models', marine_models)
        self.jedi_rendering.add_key('window_begin_iso', window_begin_iso)
        self.jedi_rendering.add_key('window_end_iso', window_end_iso)
        self.jedi_rendering.add_key('window_length', window_length)
        self.jedi_rendering.add_key('minimizer', self.config.minimizer())
        self.jedi_rendering.add_key('number_of_iterations', number_of_iterations[0])
        self.jedi_rendering.add_key('analysis_variables', self.config.analysis_variables())
        self.jedi_rendering.add_key('gradient_norm_reduction',
                                    self.config.gradient_norm_reduction())

        # Background
        # ----------
        self.jedi_rendering.add_key('horizontal_resolution', self.config.horizontal_resolution())
        self.jedi_rendering.add_key('local_background_time', local_background_time)
        self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)

        # Geometry
        # --------
        self.jedi_rendering.add_key('vertical_resolution', self.config.vertical_resolution())
        self.jedi_rendering.add_key('gsibec_nlats', gsibec_nlats)
        self.jedi_rendering.add_key('gsibec_nlons', gsibec_nlons)
        self.jedi_rendering.add_key('npx_proc', npx_proc)
        self.jedi_rendering.add_key('npy_proc', npy_proc)
        self.jedi_rendering.add_key('total_processors', self.config.total_processors(None))

        # Observations
        # ------------
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', self.config.crtm_coeff_dir(None))
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Atmosphere background error model
        # ---------------------------------
        if npx_proc is not None and npy_proc is not None:
            self.jedi_rendering.add_key('gsibec_configuration', self.config.gsibec_configuration())
            self.jedi_rendering.add_key('gsibec_nlats', gsibec_nlats)
            self.jedi_rendering.add_key('gsibec_nlons', gsibec_nlons)
            self.jedi_rendering.add_key('gsibec_npx_proc', npx_proc)
            self.jedi_rendering.add_key('gsibec_npy_proc', 6*npy_proc)

        # Background frequency is required for FGAT irrespective of the model type
        # ------------------------------------------------------------------------
        background_frequency = self.config.background_frequency()
        self.jedi_rendering.add_key('background_frequency', background_frequency)

        # Add placeholder names if mock experiment
        # ----------------------------------------
        if self.config.mock_experiment(False):
            self.jedi_rendering.add_key('experiment_root', 'experiment_root')
            self.jedi_rendering.add_key('experiment_id', 'experiment_id')
            self.jedi_rendering.add_key('cycle_dir', 'cycle_dir')

        # Use GEOS utility to generate states
        # -----------------------------------
        states = self.geos.states_generator(background_frequency, window_length,
                                            window_begin_iso, self.get_model(), marine_models)
        self.jedi_rendering.add_dynamic_key('states', states)

        # Jedi configuration file
        # -----------------------
        jedi_config_file = os.path.join(self.cycle_dir(), f'jedi_{jedi_application}_config.yaml')

        # Output log file
        # ---------------
        output_log_file = os.path.join(self.cycle_dir(), f'jedi_{jedi_application}_log.log')

        # Open the JEDI config file and fill templates
        # --------------------------------------------
        jedi_config_dict = self.jedi_rendering.render_oops_file(f'{jedi_application}', window_type,
                                                                jedi_forecast_model)

        yaml = YAML()
        yaml.default_flow_style = False

        # Write the expanded dictionary to YAML file
        # ------------------------------------------
        with open(jedi_config_file, 'w') as jedi_config_file_open:
            yaml.dump(jedi_config_dict, jedi_config_file_open)

        # Get the JEDI interface metadata
        # -------------------------------
        model_component_meta = self.jedi_rendering.render_interface_meta()

        # Compute number of processors
        # ----------------------------
        np = eval(str(model_component_meta['total_processors']))

        # Jedi executable name
        # --------------------
        jedi_executable = model_component_meta['executables'][f'{jedi_application}']
        jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle', 'build', 'bin',
                                            jedi_executable)

        # Run the JEDI executable
        # -----------------------
        if not generate_yaml_and_exit:
            self.logger.info('Running '+jedi_executable_path+' with '+str(np)+' processors.')
            run_executable(self.logger, self.cycle_dir(), np, jedi_executable_path,
                           jedi_config_file, output_log_file)
        else:
            self.logger.info('YAML generated, now exiting.')

# --------------------------------------------------------------------------------------------------
