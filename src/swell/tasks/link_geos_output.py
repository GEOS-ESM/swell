# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from datetime import datetime as dt
import os

from swell.tasks.base.task_base import taskBase
from swell.utilities.datetime import datetime_formats

# --------------------------------------------------------------------------------------------------


class LinkGeosOutput(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        """
        Linking proper GEOS output files for JEDI to ingest and produce analysis.
        This will depend on the model type (ocean vs. atmosphere), model output
        type (history vs. restart), DA method, and window length.

        Options could be offered in yamls, for instance history vs. restart.
        """

        self.current_cycle = os.path.basename(self.forecast_dir())
        src, dst = self.link_restart()

        if os.path.exists(src):
            self.geos.linker(src, dst, dst_dir=self.cycle_dir())
        else:
            self.logger.abort('Source file does not exist. JEDI will fail ' +
                              'without a proper background file.')

    # ----------------------------------------------------------------------------------------------

    def link_history(self):

        # Create GEOS history to SOCA background link
        # TODO: this will only work for 3Dvar
        # --------------------------------------------
        cc_dto = dt.strptime(self.current_cycle, datetime_formats['directory_format'])
        src = self.geos.at_cycle_geosdir('his_' + cc_dto.strftime('%Y_%m_%d_%H') + '.nc')

        dst = 'MOM6.res.' + self.current_cycle + '.nc'

        return src, dst

    # ----------------------------------------------------------------------------------------------

    def link_restart(self):

        # Create GEOS restart to SOCA background link
        # ------------------------------------------

        an_fcst_offset = self.config.analysis_forecast_window_offset()
        rst_dto = self.geos.adjacent_cycle(an_fcst_offset, return_date=True)
        seconds = str(rst_dto.hour * 3600 + rst_dto.minute * 60 + rst_dto.second)

        # Generic rst file source format for SOCA
        # ---------------------------------------
        src = self.geos.at_cycle_geosdir(['RESTART', 'MOM.res.nc'])

        # This alternate source format corresponds to optional use of Restart Record
        # parameters in AGCM.rc
        # -------------------------------------------------------------------------
        agcm_dict = self.geos.parse_rc(self.geos.at_cycle_geosdir('AGCM.rc'))

        if 'RECORD_FREQUENCY' in agcm_dict:
            src = self.geos.at_cycle_geosdir(['RESTART', rst_dto.strftime('MOM.res_Y%Y_D%j_S')
                                              + seconds + '.nc'])

        dst = 'MOM6.res.' + self.current_cycle + '.nc'

        return src, dst


# --------------------------------------------------------------------------------------------------
