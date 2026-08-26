# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
from importlib import resources
from ruamel.yaml import YAML

import swell.configuration.question_defaults as qd
from swell.tasks.base.task_base import taskBase
from swell.utilities.run_jedi_executables import run_executable
from swell.utilities.yaml_utils import replace_key

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
        window_type = self.config.resolve(qd.window_type)
        window_length = self.config.resolve(qd.window_length)
        background_time_offset = self.config.resolve(qd.background_time_offset)

        jedi_forecast_model = self.config.resolve(qd.jedi_forecast_model, default=None)
        generate_yaml_and_exit = self.config.resolve(qd.generate_yaml_and_exit, default=False)
        ensmean_only = self.config.resolve(qd.ensmean_only)
        ensmeanvariance_only = self.config.resolve(qd.ensmeanvariance_only)
        perhost = self.config.resolve(qd.perhost, default=None)

        # Set the observing system records path
        self.jedi_rendering.set_obs_records_path(self.config.resolve(qd.observing_system_records_path, default=None))

        # Compute data assimilation window parameters
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
        self.jedi_rendering.add_key('window_begin_iso', window_begin_iso)
        self.jedi_rendering.add_key('window_length', window_length)
        self.jedi_rendering.add_key('window_end_iso', window_end_iso)
        self.jedi_rendering.add_key('marine_models', self.config.resolve(qd.marine_models, default=None))
        self.jedi_rendering.add_key('analysis_variables', self.config.resolve(qd.analysis_variables))

        # Background
        self.jedi_rendering.add_key('horizontal_resolution', self.config.resolve(qd.horizontal_resolution))
        self.jedi_rendering.add_key('local_background_time', local_background_time)
        self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)
        self.jedi_rendering.add_key('ensemble_num_members', self.config.resolve(qd.ensemble_num_members))

        # Geometry
        self.jedi_rendering.add_key('vertical_resolution', self.config.resolve(qd.vertical_resolution))
        self.jedi_rendering.add_key('npx_proc', self.config.resolve(qd.npx_proc, default=None))
        self.jedi_rendering.add_key('npy_proc', self.config.resolve(qd.npy_proc, default=None))
        self.jedi_rendering.add_key('total_processors', self.config.resolve(qd.total_processors, default=None))

        # Observations
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', self.config.resolve(qd.crtm_coeff_dir, default=None))
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Ensemble hofx components
        self.jedi_rendering.add_key('ensemble_hofx_strategy', self.config.resolve(qd.ensemble_hofx_strategy))
        self.jedi_rendering.add_key('ensemble_hofx_packets', self.config.resolve(qd.ensemble_hofx_packets))

        # Ensemble Localizations
        # ------------------------------
        if self.get_model() == 'geos_atmosphere':
            self.jedi_rendering.add_key('vertical_localization_method',
                                        self.config.resolve(qd.vertical_localization_method))
            self.jedi_rendering.add_key('vertical_localization_apply_log_transform',
                                        self.config.resolve(qd.vertical_localization_apply_log_transform))
            self.jedi_rendering.add_key('vertical_localization_lengthscale',
                                        self.config.resolve(qd.vertical_localization_lengthscale))
            self.jedi_rendering.add_key('vertical_localization_ioda_vertical_coord',
                                        self.config.resolve(qd.vertical_localization_ioda_vertical_coord))
            self.jedi_rendering.add_key(
                'vertical_localization_ioda_vertical_coord_group',
                self.config.resolve(qd.vertical_localization_ioda_vertical_coord_group))
            self.jedi_rendering.add_key('vertical_localization_function',
                                        self.config.resolve(qd.vertical_localization_function))

        # Driver
        self.jedi_rendering.add_key('local_ensemble_solver', self.config.resolve(qd.local_ensemble_solver))
        self.jedi_rendering.add_key('local_ensemble_inflation_rtps',
                                    self.config.resolve(qd.local_ensemble_inflation_rtps))
        self.jedi_rendering.add_key('local_ensemble_inflation_rtpp',
                                    self.config.resolve(qd.local_ensemble_inflation_rtpp))
        self.jedi_rendering.add_key('local_ensemble_inflation_mult',
                                    self.config.resolve(qd.local_ensemble_inflation_mult))
        self.jedi_rendering.add_key('local_ensemble_save_posterior_mean',
                                    self.config.resolve(qd.local_ensemble_save_posterior_mean))
        self.jedi_rendering.add_key('local_ensemble_save_posterior_ensemble',
                                    self.config.resolve(qd.local_ensemble_save_posterior_ensemble))
        self.jedi_rendering.add_key('local_ensemble_save_posterior_mean_increment',
                                    self.config.resolve(qd.local_ensemble_save_posterior_mean_increment))
        self.jedi_rendering.add_key('local_ensemble_save_posterior_ensemble_increments',
                                    self.config.resolve(qd.local_ensemble_save_posterior_ensemble_increments))
        self.jedi_rendering.add_key('ensmean_only',
                                    self.config.resolve(qd.ensmean_only))
        self.jedi_rendering.add_key('ensmeanvariance_only',
                                    self.config.resolve(qd.ensmeanvariance_only))
        self.jedi_rendering.add_key('local_ensemble_use_linear_observer',
                                    self.config.resolve(qd.local_ensemble_use_linear_observer))
        self.jedi_rendering.add_key('skip_ensemble_hofx', self.config.resolve(qd.skip_ensemble_hofx))

        # Add placeholder names if mock experiment
        # ----------------------------------------
        if self.config.resolve(qd.mock_experiment, default=False):
            self.jedi_rendering.add_key('experiment_root', 'experiment_root')
            self.jedi_rendering.add_key('experiment_id', 'experiment_id')
            self.jedi_rendering.add_key('cycle_dir', 'cycle_dir')

        # Prevent both 'local_ensemble_save_posterior_mean' and
        # 'local_ensemble_save_posterior_ensemble' from being true
        # --------------------------------------------------------
        if self.config.resolve(qd.local_ensemble_save_posterior_mean) and \
           self.config.resolve(qd.local_ensemble_save_posterior_ensemble):
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
        jedi_config_dict = self.jedi_rendering.render_oops_file('LocalEnsembleDA',
                                                                window_type,
                                                                jedi_forecast_model)

        # Assemble localizations
        # ----------------------
        # # Vertical localizations have bug(s) - Commented out for now...
        # vertLoc = {'localization method': self.config.resolve(qd.vertical_localization_method),
        #            'apply log transformation':
        #            self.config.resolve(qd.vertical_localization_apply_log_transform),
        #            'vertical lengthscale': self.config.resolve(qd.vertical_localization_lengthscale),
        #            'ioda vertical coordinate':
        #            self.config.resolve(qd.vertical_localization_ioda_vertical_coord),
        #            'ioda vertical coordinate group':
        #            self.config.resolve(qd.vertical_localization_ioda_vertical_coord_group),
        #            'localization function': self.config.resolve(qd.vertical_localization_function)}
        # localizations = [horizLoc, vertLoc] if len(vertLoc) != 0 else [horizLoc]

        # Include ensemble localizations and halo types with each observation
        # -------------------------------------------------------------------
        localization_path = resources.files('swell').joinpath('configuration', 'jedi',
                                                              'interfaces', self.get_model(),
                                                              'observations', 'localization')

        if localization_path.exists():
            for observer in jedi_config_dict['observations']['observers']:

                # Read in safe mode
                in_yaml = YAML(typ="safe")

                # Get observation name
                observation = observer['observation_name']
                config_file = os.path.join(localization_path, f'{observation}.yaml')
                with open(config_file, 'r') as f:
                    loc_list = in_yaml.load(f)
                    horizLoc = loc_list['obs localizations']
                localization = [horizLoc]
                observer.update({'obs localizations': localization})
                observer['obs space'].update(
                    {'distribution': {'name': 'Halo', 'halo size': 5000.e3}})

        # bypass the writing of HofXs
        # ---------------------------
        bypass_HofXs = False
        if bypass_HofXs:
            for observer in jedi_config_dict['observations']['observers']:
                del observer['obs space']['obsdataout']

        # TODO: Temporary handling, change variational bc to static bc
        # -------------------------------------------------------------------
        for observer in jedi_config_dict['observations']['observers']:
            if 'obs bias' in observer:
                observer['obs bias'] = replace_key(observer['obs bias'],
                                                   "variational bc", "static bc")

        # Write the expanded dictionary to YAML file (in rt mode)
        # ------------------------------------------
        yaml = YAML()
        yaml.default_flow_style = False
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
                               jedi_config_file, output_log_file, perhost=perhost)
            else:
                run_executable(self.logger, self.cycle_dir(), np, jedi_executable_path,
                               jedi_config_file, output_log_file, perhost=perhost)
        else:
            mpi_command = "mpirun"
            if not (perhost is None or perhost == "None"):
                mpi_command += f" -perhost {perhost}"
            mpi_command += f" -np {np} {jedi_executable_path} {jedi_config_file} {output_log_file}"
            print(f'intended mpi_command = {mpi_command}')
            self.logger.info('YAML generated, now exiting.')

# --------------------------------------------------------------------------------------------------
