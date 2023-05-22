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
  'soca-3D': 'soca_var.x',
}


# --------------------------------------------------------------------------------------------------


class RunJediVariationalExecutable(RunJediExecutableBase):

    def execute(self):

        # Path to executable being run
        # ----------------------------
        window_type = self.config_get('window_type')
        npx_proc = self.config_get('npx_proc')  # Used in eval(total_processors)
        npy_proc = self.config_get('npy_proc')  # Used in eval(total_processors)
        total_processors = self.config_get('total_processors')

        # Jedi configuration file
        # -----------------------
        jedi_config_file = os.path.join(self.cycle_dir(), 'jedi_variational_config.yaml')

        # Output log file
        # ---------------
        output_log_file = os.path.join(self.cycle_dir(), 'jedi_variational_log.log')

        # Get the JEDI interface for this model component
        # -----------------------------------------------
        model_component_meta = self.jedi_rendering.render_interface_meta()
        jedi_interface = model_component_meta['jedi_interface']

        # Generate the JEDI configuration file for running the executable
        # ---------------------------------------------------------------
        jedi_config_dict = self.generate_jedi_config(self.suite(), window_type)

        with open(jedi_config_file, 'w') as jedi_config_file_open:
            yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

        # Jedi executable name
        # --------------------
        jedi_executable = interface_executable[jedi_interface + '-' + window_type]
        jedi_executable_path = os.path.join(self.experiment_path(), 'jedi_bundle', 'build',
                                            'bin', jedi_executable)
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
