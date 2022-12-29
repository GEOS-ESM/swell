# (C) Copyright 2022 United States Government as represented by the Administrator of the
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
        cycle_dir = self.config_get('cycle_dir')
        experiment_dir = self.config_get('experiment_dir')
        window_type = self.config_get('window_type')
        suite_to_run = self.config_get('suite_to_run')
        total_processors = self.config_get('total_processors')

        # Jedi configuration file
        # -----------------------
        jedi_config_file = os.path.join(cycle_dir, 'jedi_variational_config.yaml')

        # Get the JEDI interface for this model component
        # -----------------------------------------------
        model_component_meta = self.open_jedi_interface_meta_config_file()
        jedi_interface = model_component_meta['jedi_interface']

        # Generate the JEDI configuration file for running the executable
        # ---------------------------------------------------------------
        jedi_config_dict = self.generate_jedi_config(suite_to_run,window_type)

        with open(jedi_config_file, 'w') as jedi_config_file_open:
            yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

        # Jedi executable name
        # --------------------
        jedi_executable = interface_executable[jedi_interface + '-' + window_type]
        jedi_executable_path = os.path.join(experiment_dir, 'jedi_bundle', 'build', 'bin',
                                            jedi_executable)
        # Compute number of processors
        # ----------------------------
        np_string = self.use_config_to_template_string(total_processors)
        np = eval(np_string)
        # exit()
        # Run the JEDI executable
        # -----------------------
        self.run_executable(cycle_dir, np, jedi_executable_path, jedi_config_file)
        self.logger.info('Running '+jedi_executable_path+' with '+str(np)+' processors.')


# --------------------------------------------------------------------------------------------------
