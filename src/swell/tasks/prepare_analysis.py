# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import xarray as xr
from datetime import datetime as dt

from swell.tasks.base.geos_tasks_run_executable_base import *


# --------------------------------------------------------------------------------------------------


class PrepareAnalysis(GeosTasksRunExecutableBase):

    # --------------------------------------------------------------------------------------------------

    def replace_ds(self, f_ana, f_rst):

        # Update restart with analysis
        # ----------------------------
        ds2 = xr.open_dataset(f_rst, decode_cf=False)

        # This automatically closes the dataset after use
        # -----------------------------------------------
        with xr.open_dataset(f_ana, decode_cf=False) as ds1:
            ds1 = ds1.rename({'xaxis_1': 'lonh', 'yaxis_1': 'lath', 'zaxis_1': 'Layer'})
            ds1 = ds1.assign_coords(coords=ds2.coords)

            # Replace restart variables with analysis
            # ---------------------------------------
            for var in ds1.data_vars:
                ds2[var] = ds1[var]

        ds2.to_netcdf(self.at_cycle(['RESTART', 'MOM.res.nc']), mode='w')

    # --------------------------------------------------------------------------------------------------

    def execute(self):

        """
        Updates variables in restart files with analysis variables.
        """

        self.logger.info('Preparing analysis and updating restarts')

        self.cycle_dir = self.config_get('cycle_dir')
        self.an_fcst_offset = self.config_get('analysis_forecast_window_offset')

        # Current and restart time objects
        # --------------------------------
        self.current_cycle = self.config_get('current_cycle')
        self.cc_dto = dt.strptime(self.current_cycle, "%Y%m%dT%H%M%SZ")
        self.rst_dto = self.adjacent_cycle(self.cycle_dir, self.an_fcst_offset, return_date=True)

        # GEOS restarts have seconds in their filename
        # --------------------------------------------
        seconds = str(self.rst_dto.hour * 3600 + self.rst_dto.minute * 60 + self.rst_dto.second)

        f_ana = self.at_cycle('ocn.swell-3dvar_cycle.an.2021-06-21T06:00:00Z.nc')
        # f_rst = self.at_cycle('his_' + now.strftime('%Y_%m_%d_%H') + '.nc')
        f_rst = self.at_cycle(['RESTART', 'MOM.res_Y' + self.cc_dto.strftime('%Y') + '_D' + self.cc_dto.strftime('%j') + '_S' + seconds + '.nc'])

        self.replace_ds(f_ana, f_rst)

# --------------------------------------------------------------------------------------------------
