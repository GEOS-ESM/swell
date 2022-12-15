# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import subprocess
import sys
import yaml

from swell.tasks.base.task_base import taskBase


# --------------------------------------------------------------------------------------------------


interface_executable = {
  'fv3-jedi-4D': 'fv3jedi_hofx.x',
  'fv3-jedi-3D': 'fv3jedi_hofx_nomodel.x',
  'soca-4D': 'soca_hofx.x',
  'soca-3D': 'soca_hofx3d.x',
}


# --------------------------------------------------------------------------------------------------


class RunJediHofxExecutable(taskBase):

    def jedi_dictionary_iterator(self, jedi_config_dict):

        # Loop over dictionary and replace if value is a dictionary
        for key, value in jedi_config_dict.items():
            if isinstance(value, dict):
                self.jedi_dictionary_iterator(value)
            else:
                if 'TASKFILL' in value:
                    value_file = value.replace('TASKFILL', '')
                    value_dict = self.open_jedi_interface_model_config_file(value_file)
                    jedi_config_dict[key] = value_dict

    # ----------------------------------------------------------------------------------------------

    def generate_jedi_config(self, window_type):

        # Create dictionary from the templated JEDI config file
        jedi_config_dict = self.open_jedi_oops_config_file('hofx' + window_type)

        # Observations is a special case
        observations = []
        obs = self.config_get('observations')
        for ob in obs:
            # Get observation dictionary
            observations.append(self.open_jedi_interface_obs_config_file(ob))
        jedi_config_dict['observations']['observers'] = observations

        # Forecast model is a special case
        if window_type == "4D":
            model = self.config_get('model')
            model_dict = self.open_jedi_interface_model_config_file(model)
            jedi_config_dict['model'] = model_dict

        # Read configs for the rest of the dictionary
        self.jedi_dictionary_iterator(jedi_config_dict)

        return jedi_config_dict

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        # Path to executable being run
        # ----------------------------
        cycle_dir = self.config_get('cycle_dir')
        experiment_dir = self.config_get('experiment_dir')
        window_type = self.config_get('window_type')
        model = self.config_get('window_type')
        npx_proc = self.config_get('npx_proc')  # Used in eval(total_processors)
        npy_proc = self.config_get('npy_proc')  # Used in eval(total_processors)
        total_processors = self.config_get('total_processors')

        # Jedi configuration file
        # -----------------------
        jedi_config_file = os.path.join(cycle_dir, 'jedi_hofx_config.yaml')

        # Generate the JEDI configuration file for running the executable
        # ---------------------------------------------------------------
        jedi_config_dict = self.generate_jedi_config(window_type)

        with open(jedi_config_file, 'w') as jedi_config_file_open:
            yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

        # Get the JEDI interface for this model component
        # -----------------------------------------------
        model_component_meta = self.open_jedi_interface_meta_config_file()
        jedi_interface = model_component_meta['jedi_interface']

        # Jedi executable name
        # --------------------
        jedi_executable = interface_executable[jedi_interface + '-' + window_type]
        jedi_executable_path = os.path.join(experiment_dir, 'jedi_bundle', 'build', 'bin',
                                            jedi_executable)

        # Compute number of processors
        # ----------------------------
        np = eval(total_processors)

        # Run the JEDI executable
        # -----------------------
        self.logger.info('Running '+jedi_executable_path+' with '+str(np)+' processors.')

        command = ['mpirun', '-np', str(np), jedi_executable_path, jedi_config_file]

        # Move to the cycle directory
        # ---------------------------
        os.chdir(cycle_dir)

        # Execute
        # -------
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline().decode()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        rc = process.poll()

        # Abort task if the executable did not run successfully
        # -----------------------------------------------------
        if rc != 0:
            command_string = ' '.join(command)
            self.logger.abort('subprocess.run with command ' + command_string +
                              ' failed to execute.', False)

# --------------------------------------------------------------------------------------------------
