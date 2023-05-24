# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.tasks.base.run_jedi_executable_base import RunJediExecutableBase


# --------------------------------------------------------------------------------------------------


interface_executable = {
  'fv3-jedi-4D': 'fv3jedi_hofx.x',
  'fv3-jedi-3D': 'fv3jedi_hofx_nomodel.x',
  'soca-4D': 'soca_hofx.x',
  'soca-3D': 'soca_hofx3d.x',
}


# --------------------------------------------------------------------------------------------------


class RunJediHofxExecutable(RunJediExecutableBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        # Path to executable being run
        # ----------------------------
        window_type = self.config_get('window_type')
        npx_proc = self.config_get('npx_proc', None)
        npy_proc = self.config_get('npy_proc', None)
        total_processors = self.config_get('total_processors', None)
        window_length = self.config_get('window_length')
        horizontal_resolution = self.config_get('horizontal_resolution')
        vertical_resolution = self.config_get('vertical_resolution')
        crtm_coeff_dir = self.config_get('crtm_coeff_dir', None)
        window_offset = self.config_get('window_offset')
        background_time_offset = self.config_get('background_time_offset')
        observations = self.config_get('observations')

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
        self.jedi_rendering.add_key('window_length', window_length)

        # Background
        self.jedi_rendering.add_key('horizontal_resolution', horizontal_resolution)
        self.jedi_rendering.add_key('local_background_time', local_background_time)
        self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)

        # Geometry
        self.jedi_rendering.add_key('npx_proc', npx_proc)
        self.jedi_rendering.add_key('npy_proc', npy_proc)
        self.jedi_rendering.add_key('vertical_resolution', vertical_resolution)

        # Observations
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', crtm_coeff_dir)
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Jedi configuration file
        # -----------------------
        jedi_config_file = os.path.join(self.cycle_dir(), 'jedi_hofx_config.yaml')

        # Output log file
        # ---------------
        output_log_file = os.path.join(self.cycle_dir(), 'jedi_hofx_log.log')

        # Open the JEDI config file and fill initial templates
        # ----------------------------------------------------
        jedi_config_dict = self.jedi_rendering.render_oops_file(f'hofx{window_type}')

        # Perform complete template rendering
        # -----------------------------------
        self.jedi_dictionary_iterator(jedi_config_dict, window_type)

        # Write the expanded dictionary to YAML file
        # ------------------------------------------
        with open(jedi_config_file, 'w') as jedi_config_file_open:
            yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

        # Get the JEDI interface for this model component
        # -----------------------------------------------
        model_component_meta = self.jedi_rendering.render_interface_meta()
        jedi_interface = model_component_meta['jedi_interface']

        # Jedi executable name
        # --------------------
        jedi_executable = interface_executable[jedi_interface + '-' + window_type]
        jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle', 'build', 'bin',
                                            jedi_executable)

        # Compute number of processors
        # ----------------------------
        total_processors = total_processors.replace('npx_proc', str(npx_proc))
        total_processors = total_processors.replace('npy_proc', str(npy_proc))
        np = eval(total_processors)

        # Run the JEDI executable
        # -----------------------
        self.run_executable(self.cycle_dir(), np, jedi_executable_path, jedi_config_file,
                            output_log_file)
        self.logger.info('Running '+jedi_executable_path+' with '+str(np)+' processors.')

# --------------------------------------------------------------------------------------------------
