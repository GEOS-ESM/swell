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


class RunJediLetkfExecutable(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        # Jedi application name
        # ---------------------
        jedi_application = 'letkf'

        # Parse configuration
        # -------------------
        window_type = self.config.window_type()
        window_offset = self.config.window_offset()
        background_time_offset = self.config.background_time_offset()
        observations = self.config.observations()
        jedi_forecast_model = self.config.jedi_forecast_model(None)
        generate_yaml_and_exit = self.config.generate_yaml_and_exit(False)

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

        # Background
        self.jedi_rendering.add_key('horizontal_resolution', self.config.horizontal_resolution())
        self.jedi_rendering.add_key('local_background_time', local_background_time)
        self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)
        self.jedi_rendering.add_key('ensemble_num_members', self.config.ensemble_num_members())

        # Geometry
        self.jedi_rendering.add_key('vertical_resolution', self.config.vertical_resolution())
        self.jedi_rendering.add_key('npx_proc', self.config.npx_proc(None))
        self.jedi_rendering.add_key('npy_proc', self.config.npy_proc(None))
        self.jedi_rendering.add_key('total_processors', self.config.total_processors(None))

        # Observations
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', self.config.crtm_coeff_dir(None))
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Ensemble Localizations
        self.jedi_rendering.add_key('horizontal_localization_method',
                                    self.config.horizontal_localization_method())
        self.jedi_rendering.add_key('horizontal_localization_lengthscale',
                                    self.config.horizontal_localization_lengthscale())
        self.jedi_rendering.add_key('horizontal_localization_max_nobs',
                                    self.config.horizontal_localization_max_nobs())
        self.jedi_rendering.add_key('vertical_localization_method',
                                    self.config.vertical_localization_method())
        self.jedi_rendering.add_key('vertical_localization_apply_log_transform',
                                    self.config.vertical_localization_apply_log_transform())
        self.jedi_rendering.add_key('vertical_localization_lengthscale',
                                    self.config.vertical_localization_lengthscale())
        self.jedi_rendering.add_key('vertical_localization_ioda_vertical_coord',
                                    self.config.vertical_localization_ioda_vertical_coord())
        self.jedi_rendering.add_key('vertical_localization_ioda_vertical_coord_group',
                                    self.config.vertical_localization_ioda_vertical_coord_group())
        self.jedi_rendering.add_key('vertical_localization_function',
                                    self.config.vertical_localization_function())

        # Driver
        self.jedi_rendering.add_key('local_ensemble_solver', self.config.local_ensemble_solver())
        self.jedi_rendering.add_key('local_ensemble_inflation_rtps',
                                    self.config.local_ensemble_inflation_rtps())
        self.jedi_rendering.add_key('local_ensemble_inflation_rtpp',
                                    self.config.local_ensemble_inflation_rtpp())
        self.jedi_rendering.add_key('local_ensemble_inflation_mult',
                                    self.config.local_ensemble_inflation_mult())
        self.jedi_rendering.add_key('local_ensemble_save_posterior_mean',
                                    self.config.local_ensemble_save_posterior_mean())
        self.jedi_rendering.add_key('local_ensemble_save_posterior_ensemble',
                                    self.config.local_ensemble_save_posterior_ensemble())
        self.jedi_rendering.add_key('local_ensemble_save_posterior_mean_increment',
                                    self.config.local_ensemble_save_posterior_mean_increment())
        self.jedi_rendering.add_key('local_ensemble_save_posterior_ensemble_increments',
                                    self.config.local_ensemble_save_posterior_ensemble_increments())

        # Prevent both 'local_ensemble_save_posterior_mean' and
        # 'local_ensemble_save_posterior_ensemble' from being true
        # -----------
        if not self.config.local_ensemble_save_posterior_mean() ^ \
           self.config.local_ensemble_save_posterior_ensemble():
            raise ValueError("Only one of 'local_ensemble_save_posterior_mean' and\
            'local_ensemble_save_posterior_ensemble' may be true at once!")

        # Jedi configuration file
        # -----------------------
        jedi_config_file = os.path.join(self.cycle_dir(), f'jedi_{jedi_application}_config.yaml')

        # Output log file
        # ---------------
        output_log_file = os.path.join(self.cycle_dir(), f'jedi_{jedi_application}_log.log')

        # Open the JEDI config file and fill initial templates
        # ----------------------------------------------------
        jedi_config_dict = self.jedi_rendering.render_oops_file('LocalEnsembleDA')

        # Perform complete template rendering
        # -----------------------------------
        jedi_dictionary_iterator(jedi_config_dict, self.jedi_rendering, window_type, observations,
                                 jedi_forecast_model)

        # Write the expanded dictionary to YAML file
        # ------------------------------------------
        with open(jedi_config_file, 'w') as jedi_config_file_open:
            yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

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
