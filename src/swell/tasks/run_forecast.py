# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os

from swell.swell_path import get_swell_path
from swell.tasks.base.task_base import taskBase
from swell.utilities.shell_commands import run_subprocess

# --------------------------------------------------------------------------------------------------


class RunForecast(taskBase):

    def execute(self) -> None:
        """Submits gcm_run_geoscf.j via geoscf-run.sh, capturing the SLURM job log."""

        cycle_dir = self.cycle_dir()
        scratch_dir = os.path.join(cycle_dir, 'scratch')

        geoscf_run_sh = os.path.join(get_swell_path(), 'tasks', 'geoscf-run.sh')

        self.logger.info(f'Running forecast via: {geoscf_run_sh}')
        self.logger.info(f'Scratch directory: {scratch_dir}')

        env = os.environ.copy()
        env['SCRATCH_DIR'] = scratch_dir

        run_subprocess(self.logger, ['/bin/bash', geoscf_run_sh], env=env)

# --------------------------------------------------------------------------------------------------
