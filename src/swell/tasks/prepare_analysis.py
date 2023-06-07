# (C) Copyright 2023- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from datetime import datetime as dt
import netCDF4 as nc
import shutil

from swell.utilities.geos_tasks_run_executable import *


# --------------------------------------------------------------------------------------------------

# TODO: This could be restructured according to model type (MOM6, CICE etc.)
# --------------------------------------------------------------------------
SOCA_dict = {
    'hocn': 'h',
    'socn': 'Salt',
    'ssh': 'ave_ssh',
    'tocn': 'Temp',
}


class PrepareAnalysis(GeosTasksRunExecutable):

    # --------------------------------------------------------------------------------------------------

    def execute(self):

        """
        Updates variables in restart files with analysis variables.
        """

        self.logger.info('Preparing analysis and updating restarts')

        self.cycle_dir = self.config_get('cycle_dir')
        self.exp_id = self.config_get('experiment_id')
        self.soca_ana = self.config_get('analysis_variables')

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
        # f_rst = self.at_cycle_geosdir(['RESTART', rst_dto.strftime('MOM.res_Y%Y_D%j_S')
        #                                + seconds + '.nc'])
        f_rst = self.at_cycle_geosdir(['RESTART', 'MOM.res.nc'])
        self.replace_ocn(f_rst)

    # --------------------------------------------------------------------------------------------------

    def replace_ice(self, f_rst):

        '''
        placeholder for cice analysis
        '''

    # --------------------------------------------------------------------------------------------------

    def replace_ocn(self, f_rst):

        # TODO: ocean only for now, ought to update method names when
        # more model analyses (i.e., ice, bgc) are introduced.
        # TODO: combining stftime format with strings, safe practice?
        # -----------------------------------------------------------------
        # Generic analysis file format
        # ---------------------------
        f_ana = self.at_cycle('ocn.' + self.exp_id +
                              self.cc_dto.strftime('.an.%Y-%m-%dT%H:%M:%SZ.nc'))

        # Open read and write and rename dimensions
        # -----------------------------------------
        ds_ana = nc.Dataset(f_ana, 'r+')
        ds_rst = nc.Dataset(f_rst, 'r+')

        # TODO/WARNING: This method only works for read + write mode
        # ----------------------------------------------------------
        ds_ana.renameDimension('xaxis_1', 'lonh')
        ds_ana.renameDimension('yaxis_1', 'lath')
        ds_ana.renameDimension('zaxis_1', 'Layer')

        for soca_var in self.soca_ana:
            var = SOCA_dict[soca_var]
            self.logger.info(f'Updating {var} in restart')

            ds_rst.variables[var][:] = ds_ana.variables[var][:]
            ds_rst.sync()
        ds_ana.close()
        ds_rst.close()

        shutil.move(f_rst, self.at_cycle_geosdir(['RESTART', 'MOM.res.nc']))

# --------------------------------------------------------------------------------------------------
