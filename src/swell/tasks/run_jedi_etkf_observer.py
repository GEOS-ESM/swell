# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import copy
import subprocess
from ruamel.yaml import YAML

from swell.swell_path import get_swell_path
from swell.tasks.base.task_base import taskBase
from swell.utilities.yaml_utils import replace_key

# --------------------------------------------------------------------------------------------------


class RunJediEtkfObserver(taskBase):

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

        jedi_forecast_model = self.config.jedi_forecast_model(None)
        generate_yaml_and_exit = self.config.generate_yaml_and_exit(False)
        change_vbc_to_sbc = self.config.change_vbc_to_sbc(False)

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
        self.jedi_rendering.add_key('local_ensemble_use_linear_observer',
                                    self.config.local_ensemble_use_linear_observer())
        self.jedi_rendering.add_key('skip_ensemble_hofx', self.config.skip_ensemble_hofx())
        self.jedi_rendering.add_key('frac_retained_variance', self.config.frac_retained_variance())
        self.jedi_rendering.add_key('vert_loc_units', self.config.vert_loc_units())

        # Prevent both 'local_ensemble_save_posterior_mean' and
        # 'local_ensemble_save_posterior_ensemble' from being true
        # --------------------------------------------------------
        if self.config.local_ensemble_save_posterior_mean() and \
           self.config.local_ensemble_save_posterior_ensemble():
            raise ValueError("'local_ensemble_save_posterior_mean' and\
            'local_ensemble_save_posterior_ensemble' cannot be both true!")

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
                {'distribution': {'name': 'RoundRobin', 'halo size': 1500.e3}})

        # change variational bc to static bc
        # -------------------------------------------------------------------
        if change_vbc_to_sbc:
            for observer in jedi_config_dict['observations']['observers']:
                if 'obs bias' in observer:
                    observer['obs bias'] = replace_key(observer['obs bias'],
                                                       "variational bc", "static bc")
        model_component_meta = self.jedi_rendering.render_interface_meta()
        jedi_executable = model_component_meta['executables'][f'{jedi_application}']
        jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle',
                                            'build', 'bin', jedi_executable)

        # seperate each obs and write to disk
        # -------------------------------------------------------------------
        driver = jedi_config_dict['driver']
        driver['run as observer only'] = True
        driver['read HX from disk'] = False
        print(f'driver= {driver}')

        observers = jedi_config_dict["observations"]["observers"]
        npx = 1
        npy = 1
        np = 6 * npx * npy
        cmd = """
        export SLURM_MPI_TYPE=pmi2
        export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi2.so
        """
        cmd += f"cd {self.cycle_dir()} \n"
        cmd += f"rm -f log.*  logfile*  \n"
        for i, obs in enumerate(observers):
            x0 = copy.deepcopy(jedi_config_dict)
            x0["observations"]["observers"] = [obs]
            x0['geometry']['layout'] = [npx, npy]
            observation_name = obs['observation_name']
            tmp_file1 = os.path.join(self.cycle_dir(), f'diag_{observation_name}.yaml')
            tmp_file2 = os.path.join(self.cycle_dir(), f'log.diag_{observation_name}')
            with open(tmp_file1, "w") as f:
                yaml.dump(x0, f)
            cmd += (
                f"srun --exclusive --mpi=pmi2 -n {np} "
                f"{jedi_executable_path} {tmp_file1} {tmp_file2} &\n"
            )
        cmd += f"wait \n"
        print(f'nobs = {i+1}')
        np_use = (i+1) * np
        np_total = eval(str(model_component_meta['total_processors']))
        error_msg = f'{i+1} obs: each {np} cores, np_use: {np_use} vs np_avail: {np_total}'
# ygyu debug
        ##        assert np_use <= np_total, error_msg

        if not generate_yaml_and_exit:
            subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, check=True)
        else:
            print(f'intended mpi_command = {cmd}')
            self.logger.info('YAML generated, now exiting.')

# --------------------------------------------------------------------------------------------------
