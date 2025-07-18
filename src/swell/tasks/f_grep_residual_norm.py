# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import subprocess

from swell.tasks.base.task_base import taskBase

# --------------------------------------------------------------------------------------------------


class FGrepResidualNorm(taskBase):

    def execute(self) -> None:

        cycle_dir = self.cycle_dir()

        cycle_time = self.__datetime__.string_directory()
        model = self.__model__

        # Build the command
        command = ['fgrep', '"Residual norm"'] + [
                os.path.join(cycle_dir, 'jedi_variational_log.log')]
        command = ' '.join(command)

        # Run the fgrep command
        output = subprocess.run(command, capture_output=True, text=True, shell=True, check=True)
        results = output.stdout

        # Create the output directory
        out_dir = os.path.join(self.test_output, 'comparison_tests')
        os.makedirs(out_dir, exist_ok=True)

        out_name = f'residual_norms_{model}_{cycle_time}'
        if self.test_iteration is not None:
            out_name += f'_{self.test_iteration}'
        out_name += '.txt'

        # Write the output file
        out_file = os.path.join(out_dir, out_name)
        with open(out_file, 'w') as f:
            f.write(f'Residual norms output for experiment: {self.experiment_path()}:\n')
            f.write(f'Model: {model}\n')
            f.write(f'Cycle: {cycle_time}\n\n')
            f.write(f'RESULTS:\n')
            f.write(results)


# --------------------------------------------------------------------------------------------------
