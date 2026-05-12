# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import shutil
from pathlib import Path

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
            self.logger.info('Skipping publish')
            return

        # For CI tests - contain results under the run ID
        github_run_id = os.environ.get('GITHUB_RUN_ID')
        experiment_id = Path(self.experiment_id())
        if github_run_id is not None:
            experiment_id = github_run_id / experiment_id

        # Name the location after the experiment ID
        publish_location = Path(self.config.publish_directory()) / experiment_id

        self.logger.info(f'Copying comparison test results to {publish_location}')

        publish_location.mkdir(exist_ok=True, parents=True)

        # Copy the JEDI log file comparison
        log_file = Path(self.experiment_path()) / 'jedi_log_comparison.txt'
        shutil.copy(log_file, publish_location)

        eva_path = Path(self.cycle_dir()) / 'eva'

        if eva_path.is_dir():

            # Copy eva png files
            files = eva_path.rglob('**/*.png')

            out_path = publish_location / self.__datetime__.string_directory() / self.get_model()

            out_path.mkdir(exist_ok=True, parents=True)

            for file in files:
                shutil.copy(file, out_path)

# --------------------------------------------------------------------------------------------------
