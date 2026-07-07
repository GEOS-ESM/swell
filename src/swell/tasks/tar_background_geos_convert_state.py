# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import isodate
import json
import os
import tarfile

from swell.tasks.base.task_base import taskBase
from swell.utilities.datetime_util import datetime_formats


# --------------------------------------------------------------------------------------------------


class TarBackgroundGeosConvertState(taskBase):

    def execute(self):
        """Collects the resolution-converted background files produced by
        RunJediConvertStateFv3Executable and packages them into a tarball that
        mirrors the original GEOS bkgcrst tar archive.

        The output tarball:
          - Has the same filename as the input bkgcrst tar
            (e.g. x0054.bkgcrst.20211211_15z.tar) so it can be a drop-in
            replacement for the source experiment archive.
          - Contains files under their original GEOS experiment names
            (e.g. x0054.bkg_clcv_rst.20211211_2100z.nc4), recovered from the
            bkg_name_mapping.json written by GetBackgroundGeosExperiment, but
            with the experiment ID replaced by the target experiment ID if a
            target_background_experiment is configured.

        The converted files are expected to be named
        bkg_c{target_horizontal_resolution}.{bkg_time_iso}.nc4 in the cycle
        directory.
        """

        # Parse config
        # ------------
        background_experiment = self.config.background_experiment()
        target_background_experiment = self.config.target_background_experiment(
            background_experiment)
        background_time_offset = self.config.background_time_offset()
        target_horizontal_resolution = self.config.target_horizontal_resolution()
        background_window_times = self.config.background_window_times()

        # Compute the tar file name (mirrors the naming in GetBackgroundGeosExperiment)
        # ------------------------------------------------------------------------------
        background_time_offset_dur = isodate.parse_duration(background_time_offset)
        bkgr_exp_start_dto = self.cycle_time_dto() - background_time_offset_dur
        bkgr_exp_start_geos = bkgr_exp_start_dto.strftime(datetime_formats['gsi_nc_diag_format'])

        output_tar_file = os.path.join(
            self.cycle_dir(),
            f'{target_background_experiment}.bkgcrst.{bkgr_exp_start_geos}.tar'
        )

        # Load the JEDI-name -> original-name mapping saved by GetBackgroundGeosExperiment
        # ---------------------------------------------------------------------------------
        mapping_file = os.path.join(self.cycle_dir(), 'bkg_name_mapping.json')
        self.logger.info(f' Reading background name mapping from: {mapping_file}')
        with open(mapping_file, 'r') as f:
            bkg_name_mapping = json.load(f)

        # Build the output tarball
        # ------------------------
        self.logger.info(f' Creating output tarball: {output_tar_file}')
        with tarfile.open(output_tar_file, 'w') as out_tar:

            for bkg_time_offset_str in background_window_times:

                # Compute datetime for this background file
                # -----------------------------------------
                bkg_time_offset_dur = isodate.parse_duration(bkg_time_offset_str)
                bkg_time_dto = self.cycle_time_dto() + bkg_time_offset_dur
                bkg_time_iso = bkg_time_dto.strftime(datetime_formats['directory_format'])

                # The converted file written by RunJediConvertStateFv3Executable
                # ---------------------------------------------------------------
                converted_file = os.path.join(
                    self.cycle_dir(),
                    f'bkg_c{target_horizontal_resolution}.{bkg_time_iso}.nc4'
                )

                if not os.path.isfile(converted_file):
                    self.logger.abort(
                        f' Converted background file not found: {converted_file}')

                # Determine the archive member name (original GEOS filename).
                # The mapping key uses the JEDI-standard input name; replace the
                # source experiment ID with the target experiment ID.
                # ---------------------------------------------------------------
                jedi_input_name = f'bkg.{bkg_time_iso}.nc4'
                original_name = bkg_name_mapping.get(jedi_input_name, jedi_input_name)
                archive_member_name = original_name.replace(
                    background_experiment, target_background_experiment, 1)

                self.logger.info(
                    f' Adding {converted_file} to tarball as {archive_member_name}')
                out_tar.add(converted_file, arcname=archive_member_name)

        self.logger.info(f' Output tarball written: {output_tar_file}')

# --------------------------------------------------------------------------------------------------
