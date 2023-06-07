# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from datetime import datetime as dt
import os

from swell.tasks.base.task_base import taskBase

# --------------------------------------------------------------------------------------------------


class LinkGeosOutput(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        """
        Linking proper GEOS output files for JEDI to ingest and produce analysis.
        This will depend on the model type (ocean vs. atmosphere), model output
        type (history vs. restart), and DA method and window length.
        """

    # ----------------------------------------------------------------------------------------------

        #######################################################################
        # Create links for SOCA to read
        # Separate task?
        #######################################################################
        # current_cycle = self.config_get('current_cycle')
        # TODO: Is this a good approach?
        current_cycle = os.path.basename(os.path.dirname(self.cycle_dir()))
        # Leaving here, In get_cycle_dir but this should not be called if the task
        # does not receive model. so major issue is -m argument for geos at_cycle situ

        # Option #1:
        # Link restart to history output
        # TODO: this will only work for 3Dvar
        # ----------------------------------
        # cc_dto = dt.strptime(current_cycle, self.get_datetime_format())
        # src = self.geos.at_cycle_geosdir('his_' + cc_dto.strftime('%Y_%m_%d_%H') + '.nc')

        # Option #2:
        # Link restart to restart
        # GEOS restarts have seconds in their filename
        # TODO: this requires a default if the task is not attached a model (geos_ocean or atm.)
        # -------------------------------------------------------------------------------------
        an_fcst_offset = self.config_get('analysis_forecast_window_offset')
        rst_dto = self.adjacent_cycle(an_fcst_offset, return_date=True)
        seconds = str(rst_dto.hour * 3600 + rst_dto.minute * 60 + rst_dto.second)

        # Generic rst file format for SOCA
        # --------------------------------
        # src = self.geos.at_cycle_geosdir(['RESTART', rst_dto.strftime('MOM.res_Y%Y_D%j_S')
        #                              + seconds + '.nc'])
        src = self.geos.at_cycle_geosdir(['RESTART', 'MOM.res.nc'])
        dst = 'MOM6.res.' + current_cycle + '.nc'

        if os.path.exists(src):
            self.geos.linker(src, dst, dst_dir=self.cycle_dir)

# --------------------------------------------------------------------------------------------------
