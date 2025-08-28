# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import isodate
import numpy as np
import os
import netCDF4 as nc
from typing import Union
import r2d2

from datetime import timedelta, datetime as dt
from swell.tasks.base.task_base import taskBase
from swell.utilities.r2d2 import create_r2d2_config
from swell.utilities.datetime_util import datetime_formats
from r2d2 import fetch


# --------------------------------------------------------------------------------------------------


class GetObservationWithLogging(taskBase):

    """
    MODIFIED VERSION of the standard GetObservations task.

    This task performs the same logic as the original but adds detailed logging
    before each R2D2 fetch call. It prints the exact parameters being used for
    the search and the full source path of the file that R2D2 finds.
    """

    def execute(self) -> None:

        """
        Acquires observation files for a given experiment and cycle, with added logging.
        """
        # Parse config
        # ------------
        obs_experiment = self.config.obs_experiment()
        obs_providers = self.config.obs_provider()
        background_time_offset = self.config.background_time_offset()
        observations = self.config.observations()
        window_length = self.config.window_length()
        crtm_coeff_dir = self.config.crtm_coeff_dir(None)
        window_offset = self.config.window_offset()
        r2d2_local_path = self.config.r2d2_local_path()
        cycling_varbc = self.config.cycling_varbc(None)

        print(f"Configuration values:\n"
              f"  obs_experiment: {obs_experiment}\n"
              f"  obs_providers: {obs_providers}\n"
              f"  background_time_offset: {background_time_offset}\n"
              f"  observations: {observations}\n"
              f"  window_length: {window_length}\n"
              f"  crtm_coeff_dir: {crtm_coeff_dir}\n"
              f"  window_offset: {window_offset}\n"
              f"  r2d2_local_path: {r2d2_local_path}\n"
              f"  cycling_varbc: {cycling_varbc}")
