# (C) Copyright 2023- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from datetime import datetime as dt
import glob
import netCDF4 as nc
import os
import shutil

from swell.tasks.base.task_base import taskBase
from swell.utilities.datetime import datetime_formats

# --------------------------------------------------------------------------------------------------


class PrepareAnalysis(taskBase):

    # --------------------------------------------------------------------------------------------------

    def execute(self):

        """
        Updates variables in restart files with analysis variables.
        """

        self.logger.info('Preparing analysis and updating restarts')

        # This will change with different model types
        # --------------------------------
        self.jedi_rendering.add_key('total_processors', self.config.total_processors(None))
        model_component_meta = self.jedi_rendering.render_interface_meta()
        self.SOCA_dict = model_component_meta['variables']

        # Current and restart time objects
        # --------------------------------
        self.current_cycle = os.path.basename(self.forecast_dir())
        self.cc_dto = self.cycle_time_dto()
        ana_path = self.at_cycledir(['ocn.*' + self.cc_dto.strftime('.an.%Y-%m-%dT%H:%M:%SZ.nc')])

        # GEOS restarts have seconds in their filename
        # --------------------------------------------
        an_fcst_offset = self.config.analysis_forecast_window_offset()
        rst_dto = self.geos.adjacent_cycle(an_fcst_offset, return_date=True)
        seconds = str(rst_dto.hour * 3600 + rst_dto.minute * 60 + rst_dto.second)

        # Determine which models require analysis (code will fail if executed
        # without a model as "an_fcst_offset" is model dependent)
        # TODO: This could be improved with model dependent atmosphere or ocean
        # model analysis with
        # --------------------------------------------------------------------
        #

        # Generic rst file format
        # ------------------------
        f_rst = self.forecast_dir(['RESTART', 'MOM.res.nc'])

        # This alternate restart format corresponds to optional use of Restart Record
        # parameters in AGCM.rc
        # -------------------------------------------------------------------------
        agcm_dict = self.geos.parse_rc(self.forecast_dir('AGCM.rc'))

        if 'RECORD_FREQUENCY' in agcm_dict:
            f_rst = self.forecast_dir(['RESTART', rst_dto.strftime('MOM.res_Y%Y_D%j_S')
                                       + seconds + '.nc'])

        self.soca_ana = self.config.analysis_variables()
        self.replace_ocn(f_rst)

    # ----------------------------------------------------------------------------------------

    def at_cycledir(self, paths=[]):

        # Ensure what we have is a list (paths should be a list)
        # ------------------------------------------------------
        if isinstance(paths, str):
            paths = [paths]

        # Combining list of paths with cycle dir for script brevity
        # ---------------------------------------------------------
        full_path = os.path.join(self.cycle_dir(), *paths)
        return full_path

    # --------------------------------------------------------------------------------------------------

    def replace_ice(self, f_rst):

        '''
        placeholder for cice analysis
        '''
        pass

    # --------------------------------------------------------------------------------------------------

    def replace_ocn(self, f_rst):

        # TODO: combining stftime format with strings, safe practice?
        # -----------------------------------------------------------------
        # Generic analysis file format independent of exp_id
        # --------------------------------------------------
        ana_path = self.at_cycledir(['ocn.*' + self.cc_dto.strftime('.an.%Y-%m-%dT%H:%M:%SZ.nc')])

        for filepath in list(glob.glob(ana_path)):
            f_ana = filepath

        # Open read and write and rename dimensions
        # -----------------------------------------
        ds_ana = nc.Dataset(f_ana, 'r+')
        ds_rst = nc.Dataset(f_rst, 'r+')

        # WARNING: This method only works for read + write mode
        # ----------------------------------------------------------
        ds_ana.renameDimension('xaxis_1', 'lonh')
        ds_ana.renameDimension('yaxis_1', 'lath')
        ds_ana.renameDimension('zaxis_1', 'Layer')

        for soca_var in self.soca_ana:
            var = self.SOCA_dict[soca_var]
            self.logger.info(f'Updating {var} in restart')

            ds_rst.variables[var][:] = ds_ana.variables[var][:]
            ds_rst.sync()
        ds_ana.close()
        ds_rst.close()

        shutil.move(f_rst, self.forecast_dir(['RESTART', 'MOM.res.nc']))

# --------------------------------------------------------------------------------------------------
