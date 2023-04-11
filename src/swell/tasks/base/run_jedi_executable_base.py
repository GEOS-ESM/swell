# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from abc import ABC, abstractmethod
import os

from swell.tasks.base.task_base import taskBase
from swell.utilities.shell_commands import run_track_log_subprocess


# --------------------------------------------------------------------------------------------------


class RunJediExecutableBase(taskBase):

    # ----------------------------------------------------------------------------------------------

    @abstractmethod
    def execute(self):
        # This class does not execute, it provides helper function for the children
        # ------------------------------------------------------------------------
        pass

    # ----------------------------------------------------------------------------------------------

    def jedi_dictionary_iterator(self, jedi_config_dict, window_type = ''):

        # Loop over dictionary and replace if value is a dictionary, meanwhile
        # inquire list objects for dictionary items.
        # -----------------------------------------------------------

        for key, value in jedi_config_dict.items():
            if isinstance(value, dict):
                self.jedi_dictionary_iterator(value, window_type)

            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self.jedi_dictionary_iterator(item, window_type)

            else:
                if 'TASKFILL' in value:
                    value_file = value.replace('TASKFILL', '')
                    value_dict = self.open_jedi_interface_model_config_file(value_file)
                    jedi_config_dict[key] = value_dict

                elif 'SPECIAL' in value:
                    value_special = value.replace('SPECIAL', '')
                    if value_special == 'observations':
                        observations = []
                        obs = self.config_get('observations')
                        for ob in obs:
                            # Get observation dictionary
                            observations.append(self.open_jedi_interface_obs_config_file(ob))
                        jedi_config_dict[key] = observations

                    elif value_special == 'model' and window_type == '4D':
                        model = self.config_get('model')
                        model_dict = self.open_jedi_interface_model_config_file(model)
                        jedi_config_dict[key] = model_dict

    # ----------------------------------------------------------------------------------------------

    def generate_jedi_config(self, jedi_application, window_type = ''):

        # Var suite names are handled in variational executable
        # -----------------------------------------------------
        if 'var' not in jedi_application:
            jedi_application = jedi_application + window_type

        # Create dictionary from the templated JEDI config file
        # -----------------------------------------------------
        jedi_config_dict = self.open_jedi_oops_config_file(jedi_application)

        # Read configs for the rest of the dictionary
        # -------------------------------------------
        self.jedi_dictionary_iterator(jedi_config_dict, window_type)

        return jedi_config_dict

    # ----------------------------------------------------------------------------------------------

    def run_executable(self, cycle_dir, np, jedi_executable_path, jedi_config_file, output_log):

        # Run the JEDI executable
        # -----------------------
        self.logger.info('Running '+jedi_executable_path+' with '+str(np)+' processors.')

        command = ['mpirun', '-np', str(np), jedi_executable_path, jedi_config_file]

        # Move to the cycle directory
        # ---------------------------
        os.chdir(cycle_dir)

        # Run command
        # -----------
        run_track_log_subprocess(self.logger, command, output_log=output_log)


# --------------------------------------------------------------------------------------------------
