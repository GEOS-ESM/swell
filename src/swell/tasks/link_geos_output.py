# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
from netCDF4 import Dataset
import numpy as np
import xarray as xr
from typing import Tuple

from swell.tasks.base.task_base import taskBase

# --------------------------------------------------------------------------------------------------


class LinkGeosOutput(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        """
        Linking proper GEOS output files for JEDI to ingest and produce analysis.
        This will depend on the model type (ocean vs. atmosphere), model output
        type (history vs. restart), DA method, and window length.

        TODO: Options could be offered in yamls, for instance history vs. restart.
        """

        self.current_cycle = os.path.basename(os.path.dirname(self.forecast_dir()))

        # Create source and destination files for linking model output to SOCA
        # ----------------------------------
        src_dst_dict = {}

        # src, dst = self.link_mom6_restart()
        src, dst = self.link_mom6_history()
        src_dst_dict[src] = dst

        # Link CICE6 restart (iced.nc) and create SOCA input file (cice.res.nc)
        # ---------------------------------------------------------------------
        src, dst = self.prepare_cice6()
        src_dst_dict[src] = dst

        for src, dst in src_dst_dict.items():
            if os.path.exists(src):
                self.geos.linker(src, dst, self.cycle_dir())
            else:
                self.logger.abort(f'Source file {src} does not exist. JEDI will fail ' +
                                  'without a proper background file.')

    # ----------------------------------------------------------------------------------------------

    def link_mom6_history(self) -> Tuple[str, str]:

        # Create GEOS history to SOCA background link
        # TODO: this will only work for 3Dvar as FGAT requires multiple files
        # --------------------------------------------------------------------
        cc_dto = self.cycle_time_dto()
        src = self.forecast_dir('his_' + cc_dto.strftime('%Y_%m_%d_%H') + '.nc')

        dst = 'MOM6.res.' + self.current_cycle + '.nc'

        return src, dst

    # ----------------------------------------------------------------------------------------------

    def link_mom6_restart(self) -> Tuple[str, str]:

        # Create GEOS restart to SOCA background link
        # ------------------------------------------

        an_fcst_offset = self.config.analysis_forecast_window_offset()
        rst_dto = self.geos.adjacent_cycle(an_fcst_offset, return_date=True)
        seconds = str(rst_dto.hour * 3600 + rst_dto.minute * 60 + rst_dto.second)

        # Generic MOM6 rst file source format for SOCA
        # ---------------------------------------
        src = self.forecast_dir(['RESTART', 'MOM.res.nc'])

        # This alternate source format corresponds to optional use of Restart Record
        # parameters in AGCM.rc
        # -------------------------------------------------------------------------
        agcm_dict = self.geos.parse_rc(self.forecast_dir('AGCM.rc'))

        if 'RECORD_FREQUENCY' in agcm_dict:
            src = self.forecast_dir(['RESTART', rst_dto.strftime('MOM.res_Y%Y_D%j_S')
                                     + seconds + '.nc'])

        dst = 'MOM6.res.' + self.current_cycle + '.nc'

        return src, dst

    # ----------------------------------------------------------------------------------------------

    def prepare_cice6(self) -> Tuple[str, str]:

        # CICE6 input in SOCA requires aggregation of multiple variables and
        # time dimension added to the dataset.
        # --------------------------------------------------------------------
        soca2cice_vars = {'aicen': 'aicen',
                          'hicen': 'vicen',
                          'hsnon': 'vsnon'}

        # read CICE6 restart
        # -----------------
        ds = xr.open_dataset(self.forecast_dir(['RESTART', 'iced.nc']))
        nj = np.shape(ds['aicen'])[1]
        ni = np.shape(ds['aicen'])[2]

        # populate xarray with aggregated quantities
        # ------------------------------------------
        aggds = xr.merge(xr.DataArray(
                        name=varname,
                        data=np.reshape(np.sum(ds[soca2cice_vars[varname]].values, axis=0),
                                        (1, nj, ni)),
                        dims=['time', 'yaxis_1', 'xaxis_1']) for varname in soca2cice_vars.keys())

        # remove fill value
        # -----------------
        encoding = {varname: {'_FillValue': False} for varname in soca2cice_vars.keys()}

        fname_out = os.path.join(self.cycle_dir(), 'cice.res.' + self.current_cycle + '.nc')

        # save datasets
        # -------------
        aggds.to_netcdf(fname_out, format='NETCDF4', unlimited_dims='time', encoding=encoding)

        # xarray doesn't allow variables and dim that have the same name, switch to netCDF4
        # ---------------------------------------------------------------------------------
        ncf = Dataset(fname_out, 'a')
        t = ncf.createVariable('time', 'f8', ('time'))
        t[:] = 1.0
        ncf.close()

        # Generic CICE6 rst file source format for SOCA
        # ---------------------------------------
        src = self.forecast_dir(['RESTART', 'iced.nc'])
        dst = 'iced.res.' + self.current_cycle + '.nc'

        return src, dst

# --------------------------------------------------------------------------------------------------
