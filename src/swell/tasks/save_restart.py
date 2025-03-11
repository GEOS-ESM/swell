# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from datetime import datetime
import isodate
import os

from swell.tasks.base.task_base import taskBase
from swell.utilities.datetime_util import datetime_formats
from swell.utilities.file_system_operations import move_files, copy_to_dst_dir

# --------------------------------------------------------------------------------------------------


class SaveRestart(taskBase):

    def execute(self):

        """
        Moving history files to R2D2DataStore
        """

        save_folder = self.experiment_id()
        current_cycle = os.path.basename(os.path.dirname(self.forecast_dir()))
        cc_dto = self.cycle_time_dto()
        forecast_duration = 'P1DT12H'
        forecast_offset_dur = isodate.parse_duration(forecast_duration)

        beg_dto = cc_dto - isodate.parse_duration('PT12H')
        # --------------------------------------------------------------
        dst_dto = cc_dto - forecast_offset_dur

        # print(forecast_offset_dur)
        # print(forecast_duration)
        print(beg_dto)
        print(dst_dto)
        src = self.forecast_dir('his_' + cc_dto.strftime('%Y_%m_%d_%H') + '.nc')

        mainf = f'/discover/nobackup/dardag/R2D2DataStore/Local/mom6_cice6_UFS/fc/{save_folder}/global/1440x1080'

        if not os.path.exists(mainf):
            os.makedirs(mainf, exist_ok = True)
        # Convert fc_fto to 2021-06-01 format
        # -----------------------------------
        folder = dst_dto.strftime('%Y-%m-%d')

        dst_date = datetime.strftime(dst_dto, datetime_formats['iso_format'])
        dst = f'mom6_cice6_UFS.{save_folder}.fc.global.MOM.res.' + dst_date + '.P1DT12H.nc'

        dst = os.path.join(mainf, folder, dst)

        # Create RESTART folder
        # ---------------------
        if not os.path.exists(os.path.join(mainf, folder)):
            os.mkdir(os.path.join(mainf, folder))

        self.logger.info(f"Moving history to: {dst}")
        move_files(self.logger, src, dst)

        # Define other copy commands
        # --------------------------
        # Copy ice file
        src_date_fgat = datetime.strftime(beg_dto, datetime_formats['directory_format'])
        src = os.path.join(self.cycle_dir(), 'cice.res.' + src_date_fgat + '.nc')
        self.logger.info(f"Moving ice to: {dst}")
        # dst = f'ice.{save_folder}.fc.global.MOM.res.' + dst_date + '.P1DT12H.nc'
        dst = f'mom6_cice6_UFS.{save_folder}.fc.global.cice.res.' + dst_date + '.P1DT12H.nc'
        dst = os.path.join(mainf, folder, dst)
        move_files(self.logger, src, dst)

        # Copy increment file(s)
        src_inc = os.path.join(self.cycle_dir(), 'mom6_increment.nc')
        dst_inc = os.path.join(mainf, folder, f'ocn.{save_folder}.fc.global.MOM.inc.' + dst_date + '.P1DT12H.nc')
        copy_to_dst_dir(self.logger, src_inc, dst_inc)

        #ice.cice6_02.incr.2021-07-02T18:00:00Z.nc
        src_inc = os.path.join(self.cycle_dir(), f'ice.{save_folder}.incr.{cc_dto.strftime("%Y-%m-%dT%H:%M:%SZ")}.nc')
        dst_inc = os.path.join(mainf, folder, f'ice.{save_folder}.fc.global.MOM.inc.' + dst_date + '.P1DT12H.nc')
        copy_to_dst_dir(self.logger, src_inc, dst_inc)

        # # Copy bkgerrgodas.nc file
        #src_bkgerr = os.path.join(self.cycle_dir(), 'bkgerrgodas.nc')
        #dst_bkgerr = os.path.join(mainf, folder, f'mom6_cice6_UFS.{save_folder}.fc.global.MOM.bkgerr.' + dst_date + '.P1DT12H.nc')
        #copy_to_dst_dir(self.logger, src_bkgerr, dst_bkgerr)

        # # Copy oceanstats file
        src_bkgerr = os.path.join(self.forecast_dir(), 'ocean.stats.nc')
        dst_bkgerr = os.path.join(mainf, folder, f'mom6_cice6_UFS.{save_folder}.fc.global.MOM.oceanstats.' + dst_date + '.P1DT12H.nc')
        copy_to_dst_dir(self.logger, src_bkgerr, dst_bkgerr)

# --------------------------------------------------------------------------------------------------
