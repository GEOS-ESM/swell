# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import glob
import shutil
from ruamel.yaml import YAML

from swell.tasks.base.task_base import taskBase
from swell.utilities.run_jedi_executables import run_executable


# --------------------------------------------------------------------------------------------------


class RunJediEdaExecutable(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        # Jedi application name
        # ---------------------
        jedi_application = 'eda'

        # Parse configuration
        # -------------------
        window_type = self.config.window_type()
        window_length = self.config.window_length()
        forecast_length = self.config.forecast_length(window_length)
        background_time_offset = self.config.background_time_offset()
        number_of_iterations = self.config.number_of_iterations()
        jedi_forecast_model = self.config.jedi_forecast_model(None)
        generate_yaml_and_exit = self.config.generate_yaml_and_exit(False)
        perhost = self.config.perhost(None)

        # Set the observing system records path
        self.jedi_rendering.set_obs_records_path(self.config.observing_system_records_path(None))

        gsibec_nlats = self.config.gsibec_nlats(None)
        gsibec_nlons = self.config.gsibec_nlons(None)
        gsibec_configuration = self.config.gsibec_configuration(None)
        npx_proc = self.config.npx_proc(None)
        npy_proc = self.config.npy_proc(None)
        npx = self.config.npx(None)
        npy = self.config.npy(None)

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
        nmember = self.config.ensemble_num_members()
        imember = self.get_ensemble_imember()

        # Populate jedi interface templates dictionary
        # --------------------------------------------
        self.jedi_rendering.add_key('window_begin_iso', window_begin_iso)
        self.jedi_rendering.add_key('window_end_iso', window_end_iso)
        self.jedi_rendering.add_key('window_length', window_length)
        self.jedi_rendering.add_key('forecast_length', forecast_length)
        self.jedi_rendering.add_key('minimizer', self.config.minimizer())
        self.jedi_rendering.add_key('number_of_iterations', number_of_iterations[0])
        self.jedi_rendering.add_key('analysis_variables', self.config.analysis_variables())
        self.jedi_rendering.add_key('saber_central_block', self.config.saber_central_block(None))
        self.jedi_rendering.add_key('saber_outer_block', self.config.saber_outer_block(None))
        self.jedi_rendering.add_key('gradient_norm_reduction',
                                    self.config.gradient_norm_reduction())
        self.jedi_rendering.add_key('marine_models', self.config.marine_models(None))

        # Background
        # ----------
        self.jedi_rendering.add_key('horizontal_resolution', self.config.horizontal_resolution())
        self.jedi_rendering.add_key('local_background_time', local_background_time)
        self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)
        self.jedi_rendering.add_key('ensemble_num_members', self.config.ensemble_num_members())
        self.jedi_rendering.add_key('ensemble_imember', imember)

        # Geometry
        # --------
        self.jedi_rendering.add_key('vertical_resolution', self.config.vertical_resolution())
        self.jedi_rendering.add_key('gsibec_nlats', gsibec_nlats)
        self.jedi_rendering.add_key('gsibec_nlons', gsibec_nlons)
        self.jedi_rendering.add_key('npx_proc', npx_proc)
        self.jedi_rendering.add_key('npy_proc', npy_proc)
        self.jedi_rendering.add_key('npx', npx)
        self.jedi_rendering.add_key('npy', npy)
        self.jedi_rendering.add_key('total_processors', self.config.total_processors(None))

        # Observations
        # ------------
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', self.config.crtm_coeff_dir(None))
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Atmosphere background error model
        # ---------------------------------
        if gsibec_configuration is not None:
            self.jedi_rendering.add_key('gsibec_configuration', gsibec_configuration)
            self.jedi_rendering.add_key('gsibec_nlats', gsibec_nlats)
            self.jedi_rendering.add_key('gsibec_nlons', gsibec_nlons)
            self.jedi_rendering.add_key('gsibec_npx_proc', npx_proc)
            self.jedi_rendering.add_key('gsibec_npy_proc', 6*npy_proc)

        # Model
        # -----
        if window_type == '4D':
            self.jedi_rendering.add_key('background_frequency', self.config.background_frequency())

        # Jedi configuration file
        # -----------------------
        jedi_config_file = os.path.join(
            self.cycle_dir(), f'jedi_{jedi_application}{window_type}_config_mem{imember:03d}.yaml')

        # Output log file
        # ---------------
        output_log_file = os.path.join(
            self.cycle_dir(), f'jedi_{jedi_application}{window_type}_log_mem{imember:03d}.log')

        # Open the JEDI config file and fill initial templates
        # ----------------------------------------------------
        jedi_config_dict = self.jedi_rendering.render_oops_file(f'{jedi_application}{window_type}',
                                                                window_type,
                                                                jedi_forecast_model)

        # imember: specify yaml
        # ----------------------------------------------------
        if imember == 1:
            jedi_config_dict['cost function']['observations'].pop('obs perturbations', None)
        else:
            jedi_config_dict['cost function']['observations'].update({'obs perturbations': True})

        # create subdir
        mem_dir = f'analysis/mem{imember:003d}/'
        xdir = os.path.join(self.cycle_dir(), mem_dir)
        os.makedirs(xdir, exist_ok=True)

        for observer in jedi_config_dict['cost function']['observations']['observers']:
            # Get observation name
            observation = observer['observation_name']
            print(f'ob= {observation}')
            # copy obs input file to avoid multi MPI reading the same file
            files = glob.glob(os.path.join(self.cycle_dir(), f'{observation}.*'))
            for src_file in files:
                print(f'f= {src_file}')
                shutil.copy(src_file, xdir)

            if imember > 1:
                obs_cov_model = observer.get('obs error', {}).get('covariance model')
                print(f'{observation}:  obs_cov_model = {obs_cov_model}')
                if obs_cov_model and 'cross variable covariances' in obs_cov_model:
                    print(f"Found cross covariance obs: {obs_cov_model}, skip perturbation")
                else:
                    print(f"No cross variable covariance found: {observation}, Obs Error Diagonal")
                    obs_error_dict = {
                        'covariance model': 'diagonal',
                        'zero-mean perturbations': True,
                        'member': imember,
                        'number of members': nmember
                    }
                    observer.update({'obs error': obs_error_dict})
                    observer['obs space'].update({'obs perturbations seed': imember})

            hxout = observer['obs space']['obsdataout']['engine']['obsfile']
            dir1, fname = os.path.split(hxout)
            hxout = os.path.join(dir1, mem_dir, fname)
            observer['obs space']['obsdataout']['engine']['obsfile'] = hxout

            obsFileIn = observer['obs space']['obsdatain']['engine']['obsfile']
            dir1, fname = os.path.split(obsFileIn)
            obsFileIn = os.path.join(dir1, mem_dir, fname)
            observer['obs space']['obsdatain']['engine']['obsfile'] = obsFileIn

            obs_bias = observer.get('obs bias')
            if obs_bias is not None:
                File = obs_bias['input file']
                dir1, fname = os.path.split(File)
                File = os.path.join(dir1, mem_dir, fname)
                obs_bias['input file'] = File
                #
                File = obs_bias['output file']
                dir1, fname = os.path.split(File)
                File = os.path.join(dir1, mem_dir, fname)
                obs_bias['output file'] = File
                #
                File = obs_bias.get('covariance', {}).get('output file')
                if File is not None:
                    dir1, fname = os.path.split(File)
                    File = os.path.join(dir1, mem_dir, fname)
                    obs_bias['covariance']['output file'] = File
                File = obs_bias.get('covariance', {}).get('prior', {}).get('input file')
                if File is not None:
                    dir1, fname = os.path.split(File)
                    File = os.path.join(dir1, mem_dir, fname)
                    obs_bias['covariance']['prior']['input file'] = File


        print('jedi_config_dict')
        print(jedi_config_dict)
        print('end jedi_config_dict')
        exit()

        ruamel_yaml = YAML()
        ruamel_yaml.default_flow_style = False

        # Write the ordered dictionary to YAML file
        with open(jedi_config_file, 'w') as jedi_config_file_open:
            ruamel_yaml.dump(jedi_config_dict, jedi_config_file_open)

        # copy fv3-jedi dir, update dir names
        d1 = os.path.join(self.cycle_dir(), 'fv3-jedi')
        d2 = os.path.join(self.cycle_dir(), mem_dir, 'fv3-jedi')
        shutil.copytree(d1, d2, dirs_exist_ok=True)

        with open(jedi_config_file, 'r') as f:
            yaml_content = f.read()

        dir_list = ["bkg", "fv3files", "gsibec", "rcov"]
        for i in dir_list:
            j = f"fv3-jedi/{i}"
            k = f"{mem_dir}{j}"  # Result: analysis/mem002/fv3-jedi/rcov
            yaml_content = yaml_content.replace(j, k)
        with open(jedi_config_file, 'w') as f:
            f.write(yaml_content)

        # Get the JEDI interface metadata
        # -------------------------------
        model_component_meta = self.jedi_rendering.render_interface_meta()

        # Compute number of processors
        # ----------------------------
        np = eval(str(model_component_meta['total_processors']))

        # Jedi executable name
        # --------------------
        jedi_executable = model_component_meta['executables'][f'variational{window_type}']
        jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle', 'build', 'bin',
                                            jedi_executable)

        # Run the JEDI executable
        # -----------------------
        if not generate_yaml_and_exit:
            self.logger.info('Running '+jedi_executable_path+' with '+str(np)+' processors.')
            run_executable(self.logger, self.cycle_dir(), np, jedi_executable_path,
                           jedi_config_file, output_log_file, perhost)
        else:
            mpi_command = "mpirun"
            if not (perhost is None or perhost == "None"):
                mpi_command += f" -perhost {perhost}"
            mpi_command += f" -np {np} {jedi_executable_path} {jedi_config_file} {output_log_file}"
            print(f'intended mpi_command = {mpi_command}')
            self.logger.info('YAML generated, now exiting.')

# --------------------------------------------------------------------------------------------------
