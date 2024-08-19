# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from datetime import datetime as dt
import os
from netCDF4 import Dataset
import numpy as np
from typing import Dict, Tuple
import xarray as xr

from swell.utilities.datetime import datetime_formats
from swell.tasks.base.task_base import taskBase

# --------------------------------------------------------------------------------------------------


class LinkGeosOutput(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        """
        Linking proper GEOS output files for JEDI to ingest and produce analysis.
        This will depend on the model type (ocean vs. atmosphere), model output
        type (history vs. restart), DA method, and window length.
        """

        self.current_cycle = os.path.basename(os.path.dirname(self.forecast_dir()))

        # Parse configuration
        # -------------------
        self.window_type = self.config.window_type()
        self.window_length = self.config.window_length()
        self.window_offset = self.config.window_offset()
        self.window_begin_iso = self.da_window_params.window_begin_iso(self.window_offset)

        if self.window_type == '4D' or 'fgat' in self.suite_name():
            self.background_frequency = self.config.background_frequency()

        self.bkgr_time_iso, self.bkgr_time_dto = self.da_window_params.local_background_time(
            self.window_offset,
            self.window_type,
            dto=True)

        # Create source and destination files for linking model output to cycle directories
        # -----------------------------------------------------------------------------------
        self.src_dst_dict: Dict[str, Tuple[str, ...]] = {}

        if self.get_model() == 'geos_ocean' or self.get_model() == 'geos_marine':
            self.link_mom6_history(self.src_dst_dict)

            # Link CICE6 restart (iced.nc) and create SOCA input file (cice.res.nc)
            src, dst = self.prepare_cice6()
            self.src_dst_dict[src] = dst

        # Loop through the dictionary and create links
        for src, dst in self.src_dst_dict.items():
            if isinstance(dst, tuple):
                for d in dst:
                    self.geos.linker(src, d, self.cycle_dir())
            else:
                self.geos.linker(src, dst, self.cycle_dir())

    # ----------------------------------------------------------------------------------------------

    def link_mom6_history(self, src_dst_dict):

        # Create links to GEOS history for SOCA inputs
        # Depending on the DA type, there could be multiple state files to link
        # -----------------------------------------------------------------------
        if self.window_type == '4D' or 'fgat' in self.suite_name():
            states = self.geos.states_generator(self.background_frequency, self.window_length,
                                                self.window_begin_iso, self.get_model())
            # Get date information from the states dictionary, and use ocn_filename to get the
            # destination file name
            for state in states:
                date = dt.strptime(state['date'], datetime_formats['iso_format'])
                src = self.forecast_dir('his_' + date.strftime('%Y_%m_%d_%H') + '.nc')
                dst = state['ocn_filename']
                self.src_dst_dict[src] = (dst,)

            # Add the background (beginning of the window) file
            src = self.forecast_dir('his_' + self.bkgr_time_dto.strftime('%Y_%m_%d_%H') + '.nc')

            dst = 'MOM6.res.' + self.bkgr_time_iso + '.nc'

            # If src key already exists, append to the list of destination files
            if src in src_dst_dict:
                src_dst_dict[src] += (dst,)
            else:
                self.src_dst_dict[src] = (dst,)

        else:
            # Using a 3D window and hence the background is a single file, in the
            # middle of the DA window
            cc_dto = self.cycle_time_dto()
            src = self.forecast_dir('his_' + cc_dto.strftime('%Y_%m_%d_%H') + '.nc')

            dst = 'MOM6.res.' + self.current_cycle + '.nc'
            # If src key already exists, append to the list of destination files
            if src in src_dst_dict:
                src_dst_dict[src] += (dst,)
            else:
                self.src_dst_dict[src] = (dst,)


    # ----------------------------------------------------------------------------------------------

    def prepare_cice6(self):

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
