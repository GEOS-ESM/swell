# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from datetime import datetime as dt
import isodate
import os
from netCDF4 import Dataset
import numpy as np
import xarray as xr
from typing import Tuple

from swell.utilities.datetime_util import datetime_formats
from swell.tasks.base.task_base import taskBase

# --------------------------------------------------------------------------------------------------


class LinkGeosOutput(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        """
        Linking proper GEOS output files for JEDI to ingest and produce analysis.
        This will depend on the model type (ocean vs. atmosphere), model output
        type (history vs. restart), DA method, and window length.
        """

        # Parse configuration
        # -------------------
        self.marine_models = self.config.marine_models(None)
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
        self.src_dst_dict = {}

        if self.get_model() in ('geos_ocean', 'geos_marine'):
            if self.window_type == '4D' or 'fgat' in self.suite_name():
                self.link_mom6_history_4d()
            else:
                self.link_mom6_history_3d()

            if 'cice6' in self.marine_models:
                if self.window_type == '4D' or 'fgat' in self.suite_name():
                    self.link_cice6_history_4d()
                else:
                    self.link_cice6_history_3d()

                # Generic CICE6 rst file format for SOCA, this file will be
                # used for the SOCA2CICE task
                # TODO: Could use the proper background time for iced.nc with the
                # checkpoint dumps
                # ------------------------------------------------------
                src = self.forecast_dir(['RESTART', 'iced.nc'])
                dst = 'iced.res.' + self.bkgr_time_iso + '.nc'
                self.src_dst_dict[src] = dst

        # Loop through the dictionary and create links
        for src, dst in self.src_dst_dict.items():
            self.geos.linker(src, dst, self.cycle_dir())

    # ----------------------------------------------------------------------------------------------

    def link_mom6_history_4d(self) -> None:
        # Creating links to GEOS history, MOM6, for SOCA inputs
        # Depending on the DA type, there could be multiple state files to link
        # -----------------------------------------------------------------------
        states = self.geos.states_generator(self.background_frequency, self.window_length,
                                            self.window_begin_iso, self.get_model(),
                                            self.marine_models)

        # Get date information from the states dictionary, and use ocn_filename to get the
        # destination file name
        for state in states:
            date = dt.strptime(state['date'], datetime_formats['iso_format'])
            src = self.forecast_dir('his_' + date.strftime('%Y_%m_%d_%H') + '.nc')
            dst = state['ocn_filename']
            self.src_dst_dict[src] = dst

        # Add the background (beginning of the window) file
        src = self.forecast_dir('his_' + self.bkgr_time_dto.strftime('%Y_%m_%d_%H') + '.nc')
        dst = 'MOM6.res.' + self.bkgr_time_iso + '.nc'

        # Append dst to the dictionary
        self.src_dst_dict[src] = dst

    # ----------------------------------------------------------------------------------------------

    def link_mom6_history_3d(self) -> None:
        # Using a 3D window and hence the background is a single file, in the
        # middle of the DA window
        src = self.forecast_dir('his_' + self.bkgr_time_dto.strftime('%Y_%m_%d_%H') + '.nc')
        dst = 'MOM6.res.' + self.bkgr_time_iso + '.nc'

        # Append dst to the dictionary
        self.src_dst_dict[src] = dst

    # ----------------------------------------------------------------------------------------------

    def cice6_history_formatter(self,
                                src_date: dt,
                                hour_prefix: str,
                                ) -> str:

        # Extract the date part and calculate seconds for the src_history format
        date_str = src_date.strftime('%Y-%m-%d')
        seconds = src_date.hour * 3600 + src_date.minute * 60 + src_date.second

        return self.forecast_dir(f'iceh_{hour_prefix}.{date_str}-{seconds:05d}.nc')

    # ----------------------------------------------------------------------------------------------

    def cice6_history_hour_prefix(self,
                                  background_frequency: str = 'PT3H',
                                  ) -> str:
        # There is no background_frequency for 3D window so we set PT3H
        # as the default. This is defined in CICE6 input file, ice_in
        # -------------------------------------------------------------------
        # TODO: A safer alternative would be to get this information from ice_in (nml)
        # but the format is not consistent and varies according to output frequency
        # histfreq       = 'h','x','x','x','x'
        # histfreq_n     =  3 , 1 , 1 , 1 , 1

        # Convert background frequency to 02d format
        duration = isodate.parse_duration(background_frequency)
        hist_hours, remainder = divmod(duration.total_seconds(), 60*60)

        return f'{int(hist_hours):02d}h'

    # ----------------------------------------------------------------------------------------------

    def link_cice6_history_4d(self) -> None:
        # Creating links to GEOS history, CICE6, for SOCA inputs
        # Depending on the DA type, there could be multiple state files to link
        # -----------------------------------------------------------------------
        states = self.geos.states_generator(self.background_frequency, self.window_length,
                                            self.window_begin_iso, self.get_model(),
                                            self.marine_models)

        hour_prefix = self.cice6_history_hour_prefix(self.background_frequency)

        # Get date information from the states dictionary, and use ocn_filename to get the
        # destination file name
        for state in states:
            src_date = dt.strptime(state['date'], datetime_formats['iso_format'])
            src_history = self.cice6_history_formatter(src_date, hour_prefix)
            dst_history = os.path.join(self.cycle_dir(), state['ice_filename'])
            self.prepare_cice6_history(src_history, dst_history)

        # Using a 4D window; CICE6 background is at the beginning of the window
        src_history = self.cice6_history_formatter(self.bkgr_time_dto, hour_prefix)
        dst_history = os.path.join(self.cycle_dir(), 'cice.res.' + self.bkgr_time_iso + '.nc')

        self.prepare_cice6_history(src_history, dst_history)

    # ----------------------------------------------------------------------------------------------

    def link_cice6_history_3d(self) -> None:
        # Using a 3D window; CICE6 background is in the middle of the window
        hour_prefix = self.cice6_history_hour_prefix()
        src_history = self.cice6_history_formatter(self.bkgr_time_dto, hour_prefix)
        dst_history = os.path.join(self.cycle_dir(), 'cice.res.' + self.bkgr_time_iso + '.nc')

        self.prepare_cice6_history(src_history, dst_history)

    # ----------------------------------------------------------------------------------------------

    def prepare_cice6_history(self,
                              src_history: str,
                              dst_history: str,
                              ) -> None:

        # Since history already has the aggregated variables, we just need to rename
        # the dimensions and variables to match SOCA requirements
        ds = xr.open_dataset(src_history)

        # rename the dimensions to xaxis_1 and yaxis_1 and rename the variables
        ds = ds.rename({'ni': 'xaxis_1', 'nj': 'yaxis_1'})
        ds = ds.rename({'aice': 'aice_h', 'hi': 'hi_h', 'hs': 'hs_h'})

        # Save as a new file
        ds.to_netcdf(dst_history, mode='w')

    # ----------------------------------------------------------------------------------------------

    def prepare_cice6_restart(self) -> Tuple[str, str]:
        # CICE6 input in SOCA requires aggregation of multiple variables and
        # time dimension added to the dataset.
        # SOCA needs icea area (aicen), ice volume (vicen), and snow area (vsnon)
        # --------------------------------------------------------------------
        soca2cice_vars = {'aice_h': 'aicen',
                          'hi_h': 'vicen',
                          'hs_h': 'vsnon'}

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

        fname_out = os.path.join(self.cycle_dir(), 'cice.res.' + self.bkgr_time_iso + '.nc')

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
        dst = 'iced.res.' + self.bkgr_time_iso + '.nc'

        return src, dst

# --------------------------------------------------------------------------------------------------
