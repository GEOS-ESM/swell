# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import shutil
from glob import glob
from pathlib import Path
from ruamel.yaml import YAML

from swell.tasks.base.task_base import taskBase
from swell.utilities.run_jedi_executables import run_executable
from swell.utilities.yaml_utils import replace_string_value

# --------------------------------------------------------------------------------------------------


class RunJediEdaControlPertExecutable(taskBase):

    # ----------------------------------------------------------------------------------------------
    #
    # ichunk:
    #    1:nchunk: normal chunking
    #    0       : reorder chunk ana file to analysis/mem00x/ana.nc4 by symlink
    #
    def execute(self) -> None:

        # Jedi application name
        # ---------------------
        jedi_application = 'eda_control_pert'

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
        nchunk = self.config.ensemble_num_chunks()
        ichunk = self.get_ensemble_ichunk()

        # exit execute if ichunk=-1: meaning reoder analysis files
        # -------------------------------------------------------
        if ichunk == -1:
            npert = int( nmember / nchunk )
            istart = 0
            imem = 0
            for xchunk in range (1, nchunk+1):
                if xchunk == 1:
                    iend = npert -1              # mem: [0, 1 ... npert-1] : [ctrl, all pert]
                else:
                    iend = npert                 # mem: [0, 1 ... npert]   : [ctrl, all pert]
                for imem_in_chunk in range(istart, iend+1):
                    # skip extra ctrl
                    if xchunk > 1 and imem_in_chunk == 0:
                        continue
                    else:
                        imem += 1
                        dir_a = f'analysis_chunk/chunk{xchunk:03d}/mem{imem_in_chunk:03d}'
                        dir_b = f'analysis/mem{imem:03d}'
                        dir_a_full = os.path.join(self.cycle_dir(), dir_a, f'eda.ana.mem{imem_in_chunk:03d}.*.nc4')
                        # print(f'dir_a_full = {dir_a_full}')
                        fa_list = glob(dir_a_full)
                        # print(f'fa_list = {fa_list}')
                        if fa_list:
                            fa = fa_list[0]
                        else:
                            fa = ''
                            self.logger.error(
                                f"analysis files not found ichunk={ichunk}, imem_in_chunk={imem_in_chunk}")
                        print(f'fa = {fa}')
                        tail =  '.'.join(os.path.basename(fa).split('.')[-2:])
                        fb =  os.path.join(self.cycle_dir(), dir_b, f'eda.ana.mem{imem:03d}.{tail}')
                        print(f'fb = {fb}')
                        # link fa to fb
                        # Convert strings to Path objects
                        fa = Path(fa)
                        fb = Path(fb)
                        # a1. Make the directory if it does not exist
                        fb.parent.mkdir(parents=True, exist_ok=True)
                        # a2. If fb exists (or is a broken symlink), safely remove it
                        if fb.is_symlink() or fb.exists():
                            fb.unlink()
                        # a3. Create the symbolic link
                        # .resolve() gets the absolute path (like realpath in bash)
                        fb.symlink_to(fa.resolve())
                        print(f"Successfully linked {fa} to {fb}")
            return


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
        self.jedi_rendering.add_key('ensemble_num_members', nmember)
        self.jedi_rendering.add_key('ensemble_num_chunks', nchunk)
        self.jedi_rendering.add_key('ensemble_ichunk', ichunk)

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
        fname=f'jedi_{jedi_application}{window_type}_config_chunk{ichunk:03d}.yaml'
        jedi_config_file = os.path.join(self.cycle_dir(), fname)
        print(f'file = {jedi_config_file}')

        # Output log file
        # ---------------
        output_log_file = os.path.join(
            self.cycle_dir(), f"jedi_{jedi_application}{window_type}_log_chunk{ichunk:03d}.log")

        # Open the JEDI config file and fill initial templates
        # ----------------------------------------------------
        jedi_config_dict = self.jedi_rendering.render_oops_file(f'{jedi_application}',
                                                                window_type,
                                                                jedi_forecast_model)
        print(f'jedi file')


        npert = int( nmember / nchunk )
        istart = 0
        if ichunk == 1:
            iend = npert -1              # mem: [0, 1 ... npert-1] : [ctrl, all pert]
        else:
            iend = npert                 # mem: [0, 1 ... npert]   : [ctrl, all pert]

        print(f'npert = {npert}')

        # round-1: link bkg, copy obs, B and R
        # ----------------------------------------------------
        chunk_dir = f'analysis_chunk/chunk{ichunk:003d}'
        mem_temp_dir = f'analysis_chunk/chunk{ichunk:003d}/mem%mem_pad%'
        for imem in range(istart, iend+1):
            if ichunk == 1:
                id = imem + 1
            else:
                if imem == 0:
                    id = 1
                else:
                    id = npert * (ichunk -1) + imem

            # link ebkg to ebkg_chunk
            # -----------------------
            ebkg_chunk_dir = f'ebkg_chunk/chunk{ichunk:003d}/'
            xdir = os.path.join(self.cycle_dir(), ebkg_chunk_dir, f'geos.mem{imem:03d}')
            os.makedirs(xdir, exist_ok=True)

            # copy bkg files to imem dir
            f1_list = glob(os.path.join(self.cycle_dir(), f'ebkg/mem{id:03d}/geos.mem*.nc4'))
            f1  = f1_list[0]
            print(f'f1 = {f1}')
            if f1:
                f2 = os.path.basename(f1)
                f2 = f2.split('.')[2:]
                f2 = '.'.join(f2)
                f2 = os.path.join(xdir, f2)
                print(f'f2 = {f2}')
            else:
                f2 = None  # Handle the case where no file is found
                self.logger.error(f"bkg dir is empty for member id: {id}")
            if os.path.lexists(f2):
                os.remove(f2)
            os.symlink(f1, f2)

            # analysis_chunk / chunk00x / mem00y will have its own obs, B and R
            # -----------------------------------------------------------------
            mem_dir = f'analysis_chunk/chunk{ichunk:003d}/mem{imem:03d}'
            xdir = os.path.join(self.cycle_dir(), mem_dir)
            os.makedirs(xdir, exist_ok=True)

            for observer in jedi_config_dict['assimilation']['cost function']['observations']['observers']:
                # Get observation name
                observation = observer['observation_name']
                print(f'ob= {observation}')
                # copy obs input file to avoid multi MPI reading the same file
                files = glob(os.path.join(self.cycle_dir(), f'{observation}.*'))
                for src_file in files:
                    print(f'f= {src_file}')
                    shutil.copy(src_file, xdir)

            # copy fv3-jedi dir, update dir names
            d1 = os.path.join(self.cycle_dir(), 'fv3-jedi')
            d2 = os.path.join(self.cycle_dir(), mem_dir, 'fv3-jedi')
            shutil.copytree(d1, d2, dirs_exist_ok=True)

        # round-2: modify dir keys in yaml to  chunk00x / mem%mem_pad%
        # ------------------------------------------------------------
        for observer in jedi_config_dict['assimilation']['cost function']['observations']['observers']:
            # Get observation name
            observation = observer['observation_name']
            print(f'ob= {observation}')
            hxout = observer['obs space']['obsdataout']['engine']['obsfile']
            dir1, fname = os.path.split(hxout)
            hxout = os.path.join(dir1, mem_temp_dir, fname)
            observer['obs space']['obsdataout']['engine']['obsfile'] = hxout

            obsFileIn = observer['obs space']['obsdatain']['engine']['obsfile']
            dir1, fname = os.path.split(obsFileIn)
            obsFileIn = os.path.join(dir1, mem_temp_dir, fname)
            observer['obs space']['obsdatain']['engine']['obsfile'] = obsFileIn

            obs_bias = observer.get('obs bias')
            if obs_bias is not None:
                File = obs_bias['input file']
                dir1, fname = os.path.split(File)
                File = os.path.join(dir1, mem_temp_dir, fname)
                obs_bias['input file'] = File
                #
                File = obs_bias['output file']
                dir1, fname = os.path.split(File)
                File = os.path.join(dir1, mem_temp_dir, fname)
                obs_bias['output file'] = File
                #
                File = obs_bias.get('covariance', {}).get('output file')
                if File is not None:
                    dir1, fname = os.path.split(File)
                    File = os.path.join(dir1, mem_temp_dir, fname)
                    obs_bias['covariance']['output file'] = File
                #
                File = obs_bias.get('covariance', {}).get('prior', {}).get('input file')
                if File is not None:
                    dir1, fname = os.path.split(File)
                    File = os.path.join(dir1, mem_temp_dir, fname)
                    obs_bias['covariance']['prior']['input file'] = File

            observer['obs space']['obs perturbations seed shift'] = (ichunk-1)*npert

        # round-3: point dir to newly created chunks dir
        # ----------------------------------------------------
        dir_list = ["bkg", "fv3files", "gsibec", "rcov"]
        for i in dir_list:
            j = f"fv3-jedi/{i}"
            k = f"{mem_temp_dir}/{j}"  # Result: analysis/chunk00x/mem_pad/fv3-jedi/rcov
            jedi_config_dict = replace_string_value(jedi_config_dict, j, k)
            # Result: e.g., analysis/mem002/fv3-jedi/rcov

        ruamel_yaml = YAML()
        ruamel_yaml.default_flow_style = False

        # Write the ordered dictionary to YAML file
        with open(jedi_config_file, 'w') as jedi_config_file_open:
            ruamel_yaml.dump(jedi_config_dict, jedi_config_file_open)


        # Get the JEDI interface metadata
        # -------------------------------
        model_component_meta = self.jedi_rendering.render_interface_meta()

        print(f"proc = {model_component_meta['total_processors']}")
        # Compute number of processors
        # ----------------------------
        np = eval(str(model_component_meta['total_processors']))
        # modify np by  (nmember / nchunk) + 1
        if ichunk == 1:
          np = np * npert
        else:
          np = np * (npert + 1)


        # Jedi executable name
        # --------------------
        jedi_executable = model_component_meta['executables']['edaControlPert']
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
