# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import xarray as xr

# from swell.tasks.base.task_base import taskBase

from swell.tasks.base.geos_tasks_run_executable_base import *


# --------------------------------------------------------------------------------------------------


class PrepareAnalysis(GeosTasksRunExecutableBase):

    def replace_ds(self):

        fname1 = self.at_cycle('ocn.swell-3dvar_cycle.an.2021-06-21T06:00:00Z.nc')
        print(fname1)

        # This automatically closes the dataset after use
        # -----------------------------------------------
        with xr.open_dataset(fname1, decode_cf=False) as ds:
        # with xr.open_dataset(fname1) as ds:
            var = ds['ave_ssh']
            # lat = ds['xaxis_1']

        fname2 = self.at_cycle('MOM6.res.20210621T060000Z.nc')
        # print(fname2)
        # print(var)
        ds = xr.open_dataset(fname2, decode_cf=False)
        var2 = ds['ave_ssh']
        # print(var2)
        ds['ave_ssh'] = var

        # print(ds['ave_ssh'])
        print(var - var2)

    def execute(self):

        self.logger.info('PrepareAnalysis')
        self.cycle_dir = self.config_get('cycle_dir')

        self.replace_ds()

# --------------------------------------------------------------------------------------------------
