# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.swell_path import get_swell_path
from swell.tasks.base.task_base import taskBase
from swell.utilities.run_jedi_executables import jedi_dictionary_iterator, run_executable

# --------------------------------------------------------------------------------------------------


class RunJediLocalEnsembleDaExecutable(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        # Jedi application name
        # ---------------------
        jedi_application = 'localensembleda'
        jedi_ensmeanvariance_application = 'ensmeanvariance'

        # Parse configuration
        # -------------------
        window_type = self.config.window_type()
        window_length = self.config.window_length()
        window_offset = self.config.window_offset()
        background_time_offset = self.config.background_time_offset()
        observations = self.config.observations()
        jedi_forecast_model = self.config.jedi_forecast_model(None)
        generate_yaml_and_exit = self.config.generate_yaml_and_exit(False)
        ensmean_only = self.config.ensmean_only()
        ensmeanvariance_only = self.config.ensmeanvariance_only()

        # Set the observing system records path
        self.jedi_rendering.set_obs_records_path(self.config.observing_system_records_path(None))

        # Compute data assimilation window parameters
        background_time = self.da_window_params.background_time(window_offset,
                                                                background_time_offset)
        local_background_time = self.da_window_params.local_background_time(window_offset,
                                                                            window_type)
        local_background_time_iso = self.da_window_params.local_background_time_iso(window_offset,
                                                                                    window_type)
        window_begin = self.da_window_params.window_begin(window_offset)
        window_begin_iso = self.da_window_params.window_begin_iso(window_offset)
        window_end_iso = self.da_window_params.window_end_iso(window_offset, window_length)

        # Populate jedi interface templates dictionary
        # --------------------------------------------
        self.jedi_rendering.add_key('window_begin_iso', window_begin_iso)
        self.jedi_rendering.add_key('window_length', window_length)
        self.jedi_rendering.add_key('window_end_iso', window_end_iso)

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

        # Ensemble hofx components
        self.jedi_rendering.add_key('ensemble_hofx_strategy', self.config.ensemble_hofx_strategy())
        self.jedi_rendering.add_key('ensemble_hofx_packets', self.config.ensemble_hofx_packets())

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
        self.jedi_rendering.add_key('ensmean_only',
                                    self.config.ensmean_only())
        self.jedi_rendering.add_key('ensmeanvariance_only',
                                    self.config.ensmeanvariance_only())
        self.jedi_rendering.add_key('local_ensemble_use_linear_observer',
                                    self.config.local_ensemble_use_linear_observer())
        self.jedi_rendering.add_key('skip_ensemble_hofx', self.config.skip_ensemble_hofx())

        # Prevent both 'local_ensemble_save_posterior_mean' and
        # 'local_ensemble_save_posterior_ensemble' from being true
        # --------------------------------------------------------
        if self.config.local_ensemble_save_posterior_mean() or \
           self.config.local_ensemble_save_posterior_ensemble():
            raise ValueError("'local_ensemble_save_posterior_mean' and\
            'local_ensemble_save_posterior_ensemble' cannot be both true!")

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
                                 self.cycle_time_dto(), jedi_forecast_model)

        # Assemble localizations
        # ----------------------
        # # Vertical localizations have bug(s) - Commented out for now...
        # vertLoc = {'localization method': self.config.vertical_localization_method(),
        #            'apply log transformation':
        #            self.config.vertical_localization_apply_log_transform(),
        #            'vertical lengthscale': self.config.vertical_localization_lengthscale(),
        #            'ioda vertical coordinate':
        #            self.config.vertical_localization_ioda_vertical_coord(),
        #            'ioda vertical coordinate group':
        #            self.config.vertical_localization_ioda_vertical_coord_group(),
        #            'localization function': self.config.vertical_localization_function()}
        # localizations = [horizLoc, vertLoc] if len(vertLoc) != 0 else [horizLoc]

        # Include ensemble localizations and halo types with each observation
        # -------------------------------------------------------------------

        swell_path = get_swell_path()
        localization_path = os.path.join(swell_path,
                                         f'configuration/jedi/interfaces/geos_atmosphere'
                                         f'/observations/localization')
        if self.config.local_ensemble_use_linear_observer():
            for index, observation in enumerate(observations):
                # Get pointer to observer (ref to list)
                observer = jedi_config_dict['observations']['observers'][index]
                print('ob=', observation)
                config_file = os.path.join(localization_path, f'{observation}.yaml')
                with open(config_file, 'r') as f:
                    loc_list = yaml.safe_load(f)
                    horizLoc = loc_list['obs localizations']
                localization = [horizLoc]
                observer.update({'obs localizations': localization})
                observer['obs space'].update(
                    {'distribution': {'name': 'Halo', 'halo size': 5000.e3}})

        # bypass the writing of HofXs
        # -------------------------------------------------------------------

        bypass_HofXs = True
        if bypass_HofXs:
            for observer in jedi_config_dict['observations']['observers']:
                del observer['obs space']['obsdataout']

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

        jedi_ensmeanvariance_executable = model_component_meta['executables']
        [f'{jedi_ensmeanvariance_application}']
        jedi_ensmeanvariance_executable_path = os.path.join
        (self.experiment_path(), 'jedi_bundle', 'build', 'bin', jedi_ensmeanvariance_executable)
        jedi_executable = model_component_meta['executables'][f'{jedi_application}']
        jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle', 'build', 'bin',
                                            jedi_executable)

        # Run the JEDI executable
        # -----------------------
        if not generate_yaml_and_exit:
            if ensmean_only | ensmeanvariance_only:
                self.logger.info('Running ' + jedi_ensmeanvariance_executable_path +
                                 ' with '+str(np)+' processors.')
                self.logger.info('Running ensmean_only')
                run_executable(self.logger, self.cycle_dir(), np,
                               jedi_ensmeanvariance_executable_path,
                               jedi_config_file, output_log_file)
            else:
                self.logger.info('Running '+jedi_executable_path+' with '+str(np)+' processors.')
                run_executable(self.logger, self.cycle_dir(), np, jedi_executable_path,
                               jedi_config_file, output_log_file)
        else:
            self.logger.info('YAML generated, now exiting.')

# --------------------------------------------------------------------------------------------------
