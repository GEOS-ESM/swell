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


class JediCTest(taskBase):

    def execute(self) -> None:

        # Locate the soca directory
        build_dir = self.config.existing_jedi_build_directory()
        soca_dir = os.path.join(build_dir, 'soca')

        # Run the ctests
        cwd = os.getcwd()
        os.chdir(soca_dir)
        command = ['ctest', '-V', '-I']
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Record the output
        results, error = process.communicate()
        os.chdir(cwd)

        # Get the output file name
        out_name = f'jedi_ctest_results'
        if self.test_iteration is not None:
            out_name += f'-{self.test_iteration}'
        out_name += '.txt'

        # Make the output directory
        out_path = os.path.join(self.test_output, 'comparison_tests')
        os.makedirs(out_path, exist_ok=True)

        # Write the results
        with open(os.path.join(out_path, out_name), 'w') as f:
            f.write(f'JEDI CTest results for build located at: {soca_dir}\n')
            f.write(results.decode('utf-8'))

# --------------------------------------------------------------------------------------------------
