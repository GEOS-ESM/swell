# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import subprocess

from swell.tasks.base.task_base import taskBase
from swell.tasks.base.task_setup import TaskSetup
from swell.utilities.question_defaults import QuestionDefaults as qd

# --------------------------------------------------------------------------------------------------

task_name = 'JediOopsLogParser'
class Setup(TaskSetup):
    def set_attributes(self):
        self.base_name = task_name
        self.is_cycling = True
        self.is_model = True
        self.questions = [
            qd.parser_options(),
            qd.comparison_log_type()
        ]

# --------------------------------------------------------------------------------------------------

class JediOopsLogParser(taskBase):

    def fgrep_residual_norm(self, output_file):

        cycle_dir = self.cycle_dir()

        cycle_time = self.__datetime__.string_directory()
        model = self.get_model()

        log_type = self.config.comparison_log_type()

        # Build the command
        command = ['fgrep', '"Residual norm"'] + [
                os.path.join(cycle_dir, f'jedi_{log_type}_log.log')]
        command = ' '.join(command)

        # Run the fgrep command
        output = subprocess.run(command, capture_output=True, text=True, shell=True, check=True)
        results = output.stdout

        # Write the output file
        with open(output_file, 'w') as f:
            f.write(f'Residual norms output for experiment: {self.experiment_path()}:\n')
            f.write(f'Model: {model}\n')
            f.write(f'Cycle: {cycle_time}\n\n')
            f.write(f'RESULTS:\n')
            f.write(results)

    def execute(self) -> None:

        output_file = os.path.join(self.cycle_dir(), 'jedi_log_analysis.txt')

        for parser_option in self.config.parser_options(['fgrep_residual_norm']):
            if parser_option == 'fgrep_residual_norm':
                self.fgrep_residual_norm(output_file)


# --------------------------------------------------------------------------------------------------
