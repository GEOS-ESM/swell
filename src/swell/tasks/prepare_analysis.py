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
        fname2 = self.at_cycle('MOM6.res.20210621T060000Z.nc')

        ds2 = xr.open_dataset(fname2, decode_cf=False)

        with xr.open_dataset(fname1, decode_cf=False) as ds1:
            ds1 = ds1.rename({'xaxis_1': 'lonh', 'yaxis_1': 'lath','zaxis_1': 'Layer'})
            ds1 = ds1.assign_coords(coords=ds2.coords)

            # Replace variables with analysis
            # -------------------------------
            for var in ds1.data_vars:
                ds2[var] = ds1[var]

        f_out = self.at_cycle()'post_update.nc')

        if os.path.exists(f_out):
            os.remove(f_out)
        ds2.to_netcdf(f_out)

    def execute(self):

        self.logger.info('PrepareAnalysis')
        self.cycle_dir = self.config_get('cycle_dir')

        self.replace_ds()

# --------------------------------------------------------------------------------------------------
