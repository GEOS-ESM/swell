# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import os
import subprocess
import sys

from swell.tasks.base.task_base import taskBase

# --------------------------------------------------------------------------------------------------


class RunJediExecutable(taskBase):

    def execute(self):

        # Path to executable being run
        # ----------------------------
        jedi_build_path = self.config.get('jedi_build')
        jedi_executable = self.config.get('executable')
        jedi_exe_path = os.path.join(jedi_build_path, 'bin', jedi_executable)

        # Compute number of processors
        # ----------------------------
        processors = self.config.get('processors')
        np = 1
        for processor in processors:
            np = np * processor

        # Jedi configuration file
        # -----------------------
        jedi_conf_output = os.path.join(self.config.get("cycle_dir"), "jedi_config.yaml")

        # Run the JEDI executable
        # -----------------------
        self.logger.info('Running '+jedi_exe_path+' with '+str(np)+' processors.')

        command = ['mpirun', '-np', str(np), jedi_exe_path, jedi_conf_output]

        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline().decode()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        rc = process.poll()

        # Abort if the executable did not run successfully
        if rc != 0:
            command_string = ' '.join(command)
            self.logger.abort('subprocess.run with command ' + command_string +
                              ' failed to execute.')
