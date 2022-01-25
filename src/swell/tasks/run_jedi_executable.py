# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import os
import subprocess
import sys

from tide.task_base import taskBase
from tide.utils import run_subprocess

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
    print(processors)
    np = 1
    for processor in processors:
      np = np * processor

    # Jedi configuration file
    # -----------------------
    jedi_conf_output = os.path.join(self.config.get("experiment_dir"),
                                    self.config.get("current_cycle"),
                                    self.config.get("application_config")+".yaml")

    # Run the JEDI executable
    # -----------------------
    command = ['mpirun', '-np', str(np), jedi_exe_path, jedi_conf_output]
    self.logger.info('Running '+jedi_exe_path+' with '+str(np)+' processors.')
    run_subprocess(command)
    #process = subprocess.run(['mpirun', '-np', str(np), jedi_exe_path, jedi_conf_output],
    #                         stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr,
    #                         shell=False, universal_newlines=True)


#stderr=sys.stderr, stdout=sys.stdout
