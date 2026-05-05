
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


class RunJediCtests(taskBase):

    def execute(self) -> None:

        # Locate the experiment's jedi build dir, must be built or linked first
        build_dir = os.path.join(self.experiment_path(), 'jedi_bundle', 'build')

        # Identify the bundles to run ctests on
        bundles = self.config.bundles_to_run_ctests()

        for bundle in bundles:
            bundle_dir = os.path.join(build_dir, bundle)

            # Run the ctests
            cwd = os.getcwd()
            os.chdir(bundle_dir)
            command = ['ctest', '-V', '-I']
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Record the output
            results, error = process.communicate()
            os.chdir(cwd)

            # Get the output file name
            out_name = f'ctest_results-{bundle}.txt'

            # Make the output directory
            out_path = os.path.join(self.experiment_path(), 'ctests')
            os.makedirs(out_path, exist_ok=True)

            # Write the results
            with open(os.path.join(out_path, out_name), 'w') as f:
                f.write(f'CTest results for {bundle} bundle located at: {bundle_dir}\n')
                f.write(results.decode('utf-8'))

# --------------------------------------------------------------------------------------------------
