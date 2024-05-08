# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import glob
import netCDF4 as nc
import os
import shutil

from swell.utilities.shell_commands import run_subprocess
from swell.tasks.base.task_base import taskBase

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
        self.jedi_rendering.add_key('mom6_iau', self.config.mom6_iau(False))

        model_component_meta = self.jedi_rendering.render_interface_meta()
        self.SOCA_dict = model_component_meta['variables']

        # Current and restart time objects
        # --------------------------------
        self.current_cycle = os.path.basename(self.forecast_dir())
        self.cc_dto = self.cycle_time_dto()

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
        # model_components = self.get_model_components()

        # Below is SOCA specific
        # Generic analysis and increment file format independent of exp_id
        # ---------------------------------------------------------------
        ana_path = self.at_cycledir(['ocn.*' + self.cc_dto.strftime('.an.%Y-%m-%dT%H:%M:%SZ.nc')])
        incr_path = self.at_cycledir(['ocn.*' +
                                      self.cc_dto.strftime('.incr.%Y-%m-%dT%H:%M:%SZ.nc')])

        # Obtain MOM6 IAU bool
        # ----------------------
        mom6_iau = self.config.mom6_iau()

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

        if mom6_iau:
            self.mom6_increment(f_rst, ana_path, incr_path)
        else:
            self.logger.info(f'Updating restart file {f_rst} with analysis variables')
            self.replace_ocn(f_rst, ana_path)

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

    def mom6_increment(self, f_rst, ana_path, incr_path):

        # This method prepares MOM6 increment file for IAU during next cycle.
        # SOCA increment does not contain layer thickness (h) variable. Hence,
        # SOCA incr needs to be combined with the h variable from
        # the SOCA analysis file.

        for filepath in list(glob.glob(ana_path)):
            f_ana = filepath

        for filepath in list(glob.glob(incr_path)):
            f_incr = filepath

        mom6_incr = self.at_cycledir('mom6_increment.nc')
        h_ana = self.at_cycledir('h.nc')

        # Define the command to extract and append the h variable from the increment
        # file to the analysis file (-O option overwrites the existing file)
        # -----------------------------------------------------------------------
        command = f'ncks -O -v h {f_ana} {h_ana} \n' + \
            f'ncks -A -v h {h_ana} {f_incr} \n' + \
            f'mv {f_incr} {mom6_incr}'

        # Containerized run of NCO tools via CLI
        # --------------------------------------
        run_subprocess(self.logger, ['/bin/bash', '-c', command])

    # --------------------------------------------------------------------------------------------------

    def replace_ocn(self, f_rst, ana_pth):

        # TODO: This will fail for multiple restart files and no IAU
        # ----------------------------------------------------------

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
