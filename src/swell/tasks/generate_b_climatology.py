# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# -----------------------------------------------
import os
import shutil
import subprocess

import yaml

from swell.tasks.base.task_base import taskBase

# --------------------------------------------------------------------------------------------------


interface_executable = {
  'soca': 'soca_staticbinit.x',
}

# --------------------------------------------------------------------------------------------------

class GenerateBClimatology(taskBase):

    def jedi_dictionary_iterator(self, jedi_config_dict):

        # Loop over dictionary and replace if value is a dictionary
        # ---------------------------------------------------------
        for key, value in jedi_config_dict.items():
            if isinstance(value, dict):
                self.jedi_dictionary_iterator(value)
            else:
                if 'TASKFILL' in value:
                    value_file = value.replace('TASKFILL', '')
                    value_dict = self.open_jedi_interface_model_config_file(value_file)
                    jedi_config_dict[key] = value_dict

    # ----------------------------------------------------------------------------------------------

    def generate_jedi_config(self):

        # Create dictionary from the templated JEDI config file
        # ---------------------------------------------------------
        jedi_config_dict = self.open_jedi_oops_config_file('bump')

        # Read configs for the rest of the dictionary
        # -------------------------------------------
        self.jedi_dictionary_iterator(jedi_config_dict)

        return jedi_config_dict

    # ----------------------------------------------------------------------------------------------

    def execute(self):
        """Acquires B Matrix files 

            TODO: Generate Bump files for any np if not created already

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """

        total_processors = self.config_get('total_processors')
        swell_static_files = self.config_get('swell_static_files')
        horizontal_resolution = self.config_get('horizontal_resolution')
        vertical_resolution = self.config_get('vertical_resolution')
        background_error_model = self.config_get('background_error_model')
        cycle_dir = self.config_get('cycle_dir')
        experiment_dir = self.config_get('experiment_dir')

        # Get the JEDI interface for this model component
        # -----------------------------------------------
        model_component_meta = self.open_jedi_interface_meta_config_file()
        jedi_interface = model_component_meta['jedi_interface']

        if background_error_model == 'bump':
            
            # Folder name contains both horizontal and vertical resolutions 
            # ----------------------------
            resolution = horizontal_resolution + 'x' + vertical_resolution

            # Compute number of processors
            # ----------------------------
            np_string = self.use_config_to_template_string(total_processors)
            np = eval(np_string)
            
            # Get the name of the model component
            # --------------------------------
            model_component = self.get_model()

            # Load experiment file
            # --------------------
            b_dir = os.path.join(swell_static_files, 'jedi', jedi_interface, 
                        model_component, background_error_model, 'climatological', 
                            resolution,str(np))
            
            d_dir = os.path.join(cycle_dir,'background_error_model')

            self.logger.info('  Copying BUMP files from: '+b_dir)
            # shutil.copytree(b_dir, d_dir, dirs_exist_ok=True)

            # Jedi configuration file
            # -----------------------
            jedi_config_file = os.path.join(cycle_dir, 'jedi_bump_config.yaml')
            # Generate the JEDI configuration file for running the executable
            # ---------------------------------------------------------------
            jedi_config_dict = self.generate_jedi_config()
            
            with open(jedi_config_file, 'w') as jedi_config_file_open:
                yaml.dump(jedi_config_dict, jedi_config_file_open, default_flow_style=False)

            # Jedi executable name
            # --------------------
            jedi_executable = interface_executable[jedi_interface]
            jedi_executable_path = os.path.join(experiment_dir, 'jedi_bundle', 
                        'build', 'bin', jedi_executable)

            # Run the JEDI executable
            # -----------------------
            self.logger.info('Running '+jedi_executable_path+' with '+str(np)+' processors.')

            command = ['mpirun', '-np', str(np), jedi_executable_path, jedi_config_file]
            
            # Move to the cycle directory
            # ---------------------------
            os.chdir(cycle_dir)
            os.mkdir('backgrond_error_model')
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

        else:
            
            self.logger.abort('  Unknown background error model')

# --------------------------------------------------------------------------------------------------
