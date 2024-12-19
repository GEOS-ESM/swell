# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
from shutil import copy
import yaml
from typing import Optional
import subprocess
from swell.tasks.base.task_base import taskBase
from swell.utilities.run_jedi_executables import jedi_dictionary_iterator

# --------------------------------------------------------------------------------------------------


class RunJediObsfiltersExecutable(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self, ensemble_members: Optional[list] = None) -> None:

        # Jedi application name
        # ---------------------
        jedi_application = 'obsfilters'

        # Parse configuration
        # -------------------
        window_type = self.config.window_type()
        window_length = self.config.window_length()
        window_offset = self.config.window_offset()
        background_time_offset = self.config.background_time_offset()
        observations = self.config.observations()
        jedi_forecast_model = self.config.jedi_forecast_model(None)
        generate_yaml_and_exit = self.config.generate_yaml_and_exit(False)

        # Set the observing system records path
        self.jedi_rendering.set_obs_records_path(self.config.observing_system_records_path(None))

        # Compute data assimilation window parameters
        # --------------------------------------------
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
        # ----------
        self.jedi_rendering.add_key('horizontal_resolution', self.config.horizontal_resolution())
        self.jedi_rendering.add_key('local_background_time', local_background_time)
        self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)

        # Geometry
        # --------
        self.jedi_rendering.add_key('vertical_resolution', self.config.vertical_resolution())
        self.jedi_rendering.add_key('npx_proc', self.config.npx_proc(None))
        self.jedi_rendering.add_key('npy_proc', self.config.npy_proc(None))
        self.jedi_rendering.add_key('total_processors', self.config.total_processors(None))

        # Observations
        # ------------
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', self.config.crtm_coeff_dir(None))
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Model
        # -----
        if window_type == '4D':
            self.jedi_rendering.add_key('background_frequency', self.config.background_frequency())

        # Get the JEDI interface metadata
        # -------------------------------
        model_component_meta = self.jedi_rendering.render_interface_meta()

        # Compute number of processors
        # ----------------------------
        np = 1

        # Run the JEDI executable
        # ---------------------------------------------------------------------------

        # Jedi configuration file
        # -----------------------
        jedi_config_file = os.path.join(self.cycle_dir(),
                                        f'jedi_{jedi_application}_config.yaml')

        # Output log file
        # ---------------
        output_log_file = os.path.join(self.cycle_dir(), f'jedi_{jedi_application}_log.log')

        # Open the JEDI config file and fill initial templates
        # ----------------------------------------------------
        jedi_config_dict = self.jedi_rendering.render_oops_file('qc_thinning')

        # Perform complete template rendering
        # -----------------------------------
        jedi_dictionary_iterator(jedi_config_dict, self.jedi_rendering, window_type,
                                 observations, self.cycle_time_dto(), jedi_forecast_model)

        # Filter Thinning
        # ----------------------
        filter_thinning = [{'filter': 'Thinning', 'amount': 0.75,
                            'random seed': 0, 'member': 1,
                            'action': {'name': 'reduce obs space'}}]

        # Include filter_thinning into {observations: obs sapce: obs filters:}
        # -------------------------------------------------------------------
        new_dict = {'observations': []}
        for observer in jedi_config_dict['observations']['observers']:
            obs_name = observer['obs space']['name']
            obsfile = observer['obs space']['obsdatain']['engine']['obsfile']
            sim_vars = observer['obs space']['simulated variables']
            elements = obsfile.split('/')
            filename = elements[-1]
            name, extension = os.path.splitext(filename)
            new_filename = f"{name}_orig{extension}"
            new_obsfile_in = '/'.join(elements[:-1])+'/'+new_filename
            copy(obsfile, new_obsfile_in)
            obs_space = {'name': obs_name,
                         'obsdatain':
                         {'engine': {'type': 'H5File', 'obsfile': new_obsfile_in}},
                         'obsdataout': {'engine': {'type': 'H5File', 'obsfile': obsfile}},
                         'simulated variables': sim_vars}
            new_observer = {'obs space': obs_space,
                            'obs filters': filter_thinning,
                            'expectVariablesNotToExist': ['VariablesNotToExist']}
            new_dict['observations'].append(new_observer)
        del jedi_config_dict['observations']
        jedi_config_dict.update(new_dict)

        # Write the expanded dictionary to YAML file
        # ------------------------------------------
        with open(jedi_config_file, 'w') as jedi_config_file_open:
            yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

        # Jedi executable name
        # --------------------
        jedi_executable = \
            model_component_meta['executables'][f'{jedi_application}']
        jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle',
                                            'build', 'bin', jedi_executable)

        # Run the JEDI executable
        # -----------------------
        if not generate_yaml_and_exit:
            self.logger.info('Running '+jedi_executable_path+' with '+str(np)+' processors.')
            command = (f'mpirun -np 1 {jedi_executable_path} ' +
                       f'{jedi_config_file} {output_log_file}')
            print('cmd=', command)
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            print("Output:", result.stdout)
            print("Return code:", result.returncode)
        else:
            self.logger.info('YAML generated, now exiting.')
# --------------------------------------------------------------------------------------------------
