# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os

from swell.tasks.base.task_base import taskBase
from swell.utilities.shell_commands import run_subprocess

# --------------------------------------------------------------------------------------------------


class RunForecast(taskBase):

    def execute(self) -> None:
        """Submits the GCM forecast job script via sbatch."""

        cycle_dir = self.cycle_dir()
        gcm_run_script = os.path.join(cycle_dir, 'scratch', 'gcm_run_geoscf.j')

        self.logger.info(f'Submitting forecast job and waiting for completion: {gcm_run_script}')
        run_subprocess(self.logger, ['sbatch', '--wait', gcm_run_script])

# --------------------------------------------------------------------------------------------------
