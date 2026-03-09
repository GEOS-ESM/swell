# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
from ruamel.yaml import YAML

from swell.swell_path import get_swell_path
from swell.tasks.base.task_base import taskBase
from swell.utilities.run_jedi_executables import run_executable
from swell.utilities.yaml_utils import replace_key

# --------------------------------------------------------------------------------------------------


class RunJediEtkfSolver(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        # Jedi application name
        # ---------------------
        jedi_application = 'localensembleda'

        # Parse configuration
        # -------------------
        window_type = self.config.window_type()
        window_length = self.config.window_length()
        background_time_offset = self.config.background_time_offset()
        change_vbc_to_sbc = self.config.change_vbc_to_sbc(False)

        jedi_forecast_model = self.config.jedi_forecast_model(None)
        generate_yaml_and_exit = self.config.generate_yaml_and_exit(False)

        # Set the observing system records path
        self.jedi_rendering.set_obs_records_path(self.config.observing_system_records_path(None))

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
        self.jedi_rendering.add_key('vertical_localization_unit',
                                    self.config.vertical_localization_unit())
        self.jedi_rendering.add_key('vertical_localization_lengthscale',
                                    self.config.vertical_localization_lengthscale())
        self.jedi_rendering.add_key('vertical_localization_frac_retained_variance',
                                    self.config.vertical_localization_frac_retained_variance())
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
        self.jedi_rendering.add_key('local_ensemble_use_linear_observer',
                                    self.config.local_ensemble_use_linear_observer())
        self.jedi_rendering.add_key('skip_ensemble_hofx', self.config.skip_ensemble_hofx())

        # Prevent both 'local_ensemble_save_posterior_mean' and
        # 'local_ensemble_save_posterior_ensemble' from being true
        # --------------------------------------------------------
        if self.config.local_ensemble_save_posterior_mean() and \
           self.config.local_ensemble_save_posterior_ensemble():
            raise ValueError("'local_ensemble_save_posterior_mean' and\
            'local_ensemble_save_posterior_ensemble' cannot be both true!")

        # Jedi configuration file
        # -----------------------
        jedi_config_file = os.path.join(self.cycle_dir(), f'jedi_etkf_solver_config.yaml')

        # Output log file
        # ---------------
        output_log_file = os.path.join(self.cycle_dir(), f'jedi_etkf_solver_log.log')

        # Open the JEDI config file and fill initial templates
        # ----------------------------------------------------
        jedi_config_dict = self.jedi_rendering.render_oops_file('LocalEnsembleDA',
                                                                window_type,
                                                                jedi_forecast_model)

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
        yaml = YAML()
        # update localizations in dict
        for observer in jedi_config_dict['observations']['observers']:
            # Get observation name
            observation_name = observer['observation_name']
            config_file = os.path.join(localization_path, f'{observation_name}.yaml')
            with open(config_file, 'r') as f:
                loc_list = yaml.load(f)
                horizLoc = loc_list['obs localizations']
            localization = [horizLoc]
            observer.update({'obs localizations': localization})
            observer['obs space'].update(
                {'distribution': {'name': 'Halo', 'halo size': 1500.e3}})

        # change variational bc to static bc
        # -------------------------------------------------------------------
        if change_vbc_to_sbc:
            for observer in jedi_config_dict['observations']['observers']:
                if 'obs bias' in observer:
                    observer['obs bias'] = replace_key(observer['obs bias'],
                                                       "variational bc", "static bc")

        driver = jedi_config_dict['driver']
        driver['read HX from disk'] = True
        driver['run as observer only'] = False
        print(f'driver= {driver}')

        observers = jedi_config_dict["observations"]["observers"]
        for i, obs in enumerate(observers):
            observation_name = obs['observation_name']
            obs_file_read = obs['obs space']['obsdataout']['engine']['obsfile']
            print(f'\n obs_file_read = {obs_file_read}')
            obs['obs space']['obsdatain']['engine']['obsfile'] = obs_file_read
            dir_path = os.path.dirname(obs_file_read)
            file_name = os.path.basename(obs_file_read)
            obs['obs space']['obsdataout']['engine']['obsfile'] = os.path.join(dir_path, 'solver.' + file_name)

        with open(jedi_config_file, 'w') as f:
            yaml.dump(jedi_config_dict, f)

        model_component_meta = self.jedi_rendering.render_interface_meta()
        jedi_executable = model_component_meta['executables'][f'{jedi_application}']
        jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle', 'build', 'bin',
                                            jedi_executable)
        np = eval(str(model_component_meta['total_processors']))
        perhost = self.config.perhost(None)
        if not generate_yaml_and_exit:
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
