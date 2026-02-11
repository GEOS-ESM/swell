# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import re
import glob
import shutil

from swell.tasks.base.task_base import taskBase

# --------------------------------------------------------------------------------------------------


class PublishComparisons(taskBase):

    '''Copies releveant text files and plots to a specified "publish location".

    If 'publish_directory' is None, the files will not be copied.
    '''

    def execute(self) -> None:

        # Output path base to copy files to
        publish_directory = self.config.publish_directory(None)

        # Skip this task if there is no publish directory
        if publish_directory is None:
            return

        # For CI tests - contain results under the run ID
        github_run_id = os.environ.get('GITHUB_RUN_ID')
        experiment_id = self.experiment_id()
        if github_run_id is not None:
            experiment_id = os.path.join(github_run_id, experiment_id)

        # Name the location after the experiment ID
        publish_location = os.path.join(self.config.publish_directory(), experiment_id)

        os.makedirs(publish_location, exist_ok=True)

        # Copy the JEDI log file comparison
        log_file = os.path.join(self.experiment_path(), 'jedi_log_comparison.txt')
        shutil.copy(log_file, publish_location)

        # Get the cycles
        cycle_path = os.path.join(self.experiment_path(), 'run')
        cycles = [d for d in os.listdir(cycle_path) if re.match('[0-9]*T[0-9]*Z', d)]

        for cycle in cycles:
            for model in self.config.model_components():
                if os.path.isdir(os.path.join(cycle_path, cycle, model, 'eva')):

                    # Copy eva png files
                    files = glob.glob(os.path.join(cycle_path, cycle, model,
                                                   'eva', '**', '*.png'), recursive=True)

                    out_path = os.path.join(publish_location, cycle, model)

                    os.makedirs(out_path, exist_ok=True)

                    for file in files:
                        shutil.copy(file, out_path)

# --------------------------------------------------------------------------------------------------
