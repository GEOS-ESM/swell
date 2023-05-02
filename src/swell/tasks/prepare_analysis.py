# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from datetime import datetime as dt
import xarray as xr

from swell.tasks.base.geos_tasks_run_executable_base import *


# --------------------------------------------------------------------------------------------------


class PrepareAnalysis(GeosTasksRunExecutableBase):

    # --------------------------------------------------------------------------------------------------

    def replace_ocn(self, f_rst):

        # TODO: ocean only for now, ought to update method names when
        # more model analyses (i.e., ice, bgc) are introduced.
        # TODO: combining stftime format with strings, safe practice?
        # -----------------------------------------------------------------
        # Generic analysis file format
        # ---------------------------
        f_ana = self.at_cycle('ocn.' + self.exp_id + self.cc_dto.strftime('.an.%Y-%m-%dT%H:%M:%SZ.nc'))

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
        self.exp_id = self.config_get('experiment_id')

        # Current and restart time objects
        # --------------------------------
        self.current_cycle = self.config_get('current_cycle')
        self.cc_dto = dt.strptime(self.current_cycle, self.get_datetime_format())

        # GEOS restarts have seconds in their filename
        # --------------------------------------------
        an_fcst_offset = self.config_get('analysis_forecast_window_offset')
        rst_dto = self.adjacent_cycle(self.cycle_dir, an_fcst_offset, return_date=True)
        seconds = str(rst_dto.hour * 3600 + rst_dto.minute * 60 + rst_dto.second)

        # Generic rst file format
        # ------------------------
        f_rst = self.at_cycle(['RESTART', rst_dto.strftime('MOM.res_Y%Y_D%j_S') + seconds + '.nc'])
        self.replace_ocn(f_rst)

# --------------------------------------------------------------------------------------------------
