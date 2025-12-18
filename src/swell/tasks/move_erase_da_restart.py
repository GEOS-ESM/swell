# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import glob
import isodate
import os
import re
import shutil
from typing import Union

from swell.tasks.base.task_base import taskBase
from swell.utilities.file_system_operations import move_files

# --------------------------------------------------------------------------------------------------


class MoveEraseDaRestart(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        """
        Moving restart files (i.e., _checkpoint) to the next cycle directory.
        One way is using AGCM.rc checkpoint option. This creates time stamped _checkpoint
        files requiring additional filename handling.

        The reason this is a separate task than MoveForecast is that the use of
        "window_length" will require model argument input.
        """

        self.logger.info('Moving GEOS restarts to the next forecast cycle')

        # Obtain MOM6 IAU bool
        # ----------------------
        self.mom6_iau = self.config.mom6_iau()
        self.jedi_rendering.add_key('mom6_iau', self.config.mom6_iau(False))

        # Create cycle_dir and RESTART
        # ----------------------------
        os.makedirs(self.forecast_dir('RESTART'), 0o755, exist_ok=True)

        # Move and rename files in the next forecast directory
        # ----------------------------------------------
        self.move_restarts()
        self.move_marine_restarts()
        self.geos.rename_checkpoints(self.forecast_dir())

    # ----------------------------------------------------------------------------------------------

    def move_restarts(self) -> None:

        # Move restarts (checkpoints) in the current cycle dir
        # ------------------------------------------------------
        self.logger.info('GEOS restarts are being moved to the next forecast dir')

        src = self.forecast_dir(['scratch', '*_checkpoint'])

        # This alternate source format corresponds to optional use of Restart Record
        # parameters in AGCM.rc
        # -------------------------------------------------------------------------
        agcm_dict = self.geos.parse_rc(self.forecast_dir('AGCM.rc'))

        if 'RECORD_FREQUENCY' in agcm_dict:
            window_length = self.config.window_length()
            an_fcst_offset = self.da_window_params.analysis_forecast_window_offset(window_length)
            rst_dto = self.geos.adjacent_cycle(an_fcst_offset, return_date=True)

            self.logger.info('Using _checkpoint restarts with timestamps')
            src = self.forecast_dir(['scratch', rst_dto.strftime('*_checkpoint.%Y%m%d_%H%Mz.nc4')])

        for filepath in list(glob.glob(src)):
            filename = os.path.basename(filepath).split('.')[0]
            move_files(self.logger, filepath, self.forecast_dir(filename))

    def move_marine_restarts(self) -> None:
        ''' Moving marine model restart files to the next forecast directory. '''

        # Create a dictionary of src/dst for the single files
        # ---------------------------------------------------
        src_dst = {'scratch/tile.bin': '',
                   'scratch/RESTART/iced.nc': 'RESTART',
                   }

        for src, dst in src_dst.items():
            dst = os.path.join(dst, os.path.basename(src))
            move_files(self.logger, self.forecast_dir(src), self.forecast_dir(dst))

        # Having multiple restart outputs in MOM6 is hard coded and inevitable for high res
        # simulations. MOM restart for the next cycle should be at the beginning of the
        # current DA window.

        # Due to the mismatch between source & destination filenames a dictionary was created
        # to handle these differences.
        # --------------------------------------------------------------------------
        src_dst_dict = {}

        # This alternate source format corresponds to optional use of Restart Record
        # parameters in AGCM.rc
        # -------------------------------------------------------------------------
        agcm_dict = self.geos.parse_rc(self.forecast_dir('AGCM.rc'))

        if 'RECORD_FREQUENCY' in agcm_dict:

            window_length = self.config.window_length()

            an_fcst_offset = self.da_window_params.analysis_forecast_window_offset(window_length)
            rst_dto = self.geos.adjacent_cycle(an_fcst_offset, return_date=True)
            seconds = rst_dto.hour * 3600 + rst_dto.minute * 60 + rst_dto.second

            # Ensure seconds is a string with 5 digits
            seconds_str = f"{seconds:05d}"
            rst_pattern = rst_dto.strftime('MOM.res_Y%Y_D%j_S') + seconds_str + '*.nc'
            rst_files = os.path.join(self.forecast_dir('scratch/RESTART'), rst_pattern)

            for filepath in list(glob.glob(rst_files)):
                filename = os.path.basename(filepath)

                # Use re.sub to remove the time pattern from the string
                # -----------------------------------------------------
                time_pattern = rst_dto.strftime('_Y%Y_D%j_S') + seconds_str
                filenext = re.sub(time_pattern, "", filename)

                dst_path = os.path.join(self.forecast_dir('RESTART'), filenext)
                src_dst_dict.update({
                        filepath: dst_path,
                })

        else:
            rst_files = self.forecast_dir(['scratch', 'RESTART', 'MOM.res*nc'])

            for filepath in list(glob.glob(rst_files)):
                filename = os.path.basename(filepath)
                src_dst_dict.update({
                        filepath: self.forecast_dir(['RESTART', filename]),
                })

        # If the src/dst dict is empty, abort run as something is messed up
        # -----------------------------------------------------------------
        if (len(src_dst_dict) == 0):
            self.logger.abort(f'Restart file(s) do not exist. This indicates ' +
                              'an issue with the restart outputs and/or RECORD_FREQUENCY inputs.')

        # Include the increment file if IAU is active
        # -------------------------------------------
        if (self.mom6_iau):
            src_dst_dict.update({
                os.path.join(self.cycle_dir(), 'mom6_increment.nc'):
                    self.forecast_dir(['RESTART', 'mom6_increment.nc'])
            })

        # Check if there are any .rcx files to be moved and include them (history restarts)
        # ------------------------------------------------------------
        rcx_files = os.path.join(self.forecast_dir('scratch'), '*.rcx')
        for filepath in list(glob.glob(rcx_files)):
            filename = os.path.basename(filepath)
            dst_path = os.path.join(self.forecast_dir(), filename)
            src_dst_dict.update({
                    filepath: dst_path,
            })

        for src, dst in src_dst_dict.items():
            move_files(self.logger, src, dst)

# --------------------------------------------------------------------------------------------------
