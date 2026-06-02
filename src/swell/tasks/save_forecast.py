# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from datetime import datetime as dt
from datetime import timedelta
import isodate
import os
from r2d2 import store


from swell.tasks.base.task_base import taskBase
from swell.utilities.datetime_util import datetime_formats
from swell.utilities.r2d2 import load_r2d2_credentials


# --------------------------------------------------------------------------------------------------


class StoreBackground(taskBase):

    def execute(self) -> None:

        """Store background files for a given experiment and cycle in R2D2

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """

        # Load R2D2 credentials
        # ---------------------
        load_r2d2_credentials(self.logger, self.platform())

        # Current cycle time object
        # -------------------------
        current_cycle_dto = dt.strptime(self.cycle_time(), datetime_formats['iso_format'])

        # Get duration into forecast for first background file
        # ----------------------------------------------------
        bkg_steps = []

        # Parse config
        window_type = self.config.window_type()
        window_length = self.config.window_length()
        background_experiment = self.config.background_experiment()
        background_frequency = self.config.background_frequency()

        # Position relative to center of the window where forecast starts
        forecast_offset = self.da_window_params.analysis_forecast_window_offset(window_length)

        # Convert to datetime durations
        window_length_dur = isodate.parse_duration(window_length)
        window_offset_dur = self.da_window_params.window_offset(window_length, dto=True)
        forecast_offset_dur = isodate.parse_duration(forecast_offset)

        # Depending on window type get the time of the background
        if window_type == "3D":
            # Single background at the middle of the window
            fcst_length = window_length_dur - forecast_offset_dur
            forecast_start_time = current_cycle_dto - fcst_length
        elif window_type == "4D":
            # Background at the start of the window
            fcst_length = window_length_dur - forecast_offset_dur - window_offset_dur
            forecast_start_time = current_cycle_dto - window_offset_dur - fcst_length

        # Convert to ISO duration string
        fcst_length_iso = isodate.duration_isoformat(fcst_length)
        bkg_steps.append(fcst_length_iso)

        # If background is provided though files get all backgrounds
        # ----------------------------------------------------------
        if window_type == "4D":

            bkg_freq_dur = isodate.parse_duration(background_frequency)

            # Check for a sensible frequency
            if (window_length_dur/bkg_freq_dur) % 2:
                self.logger.abort('Window length not divisible by background frequency')

            # Loop over window
            start_date = current_cycle_dto - window_offset_dur
            final_date = current_cycle_dto + window_offset_dur

            loop_date = start_date + bkg_freq_dur

            while loop_date <= final_date:
                duration_in = loop_date - start_date + fcst_length
                bkg_steps.append(isodate.duration_isoformat(duration_in))
                loop_date += bkg_freq_dur

        # Loop over background files in the R2D2 config and store
        # -------------------------------------------------------
        self.logger.info('Background steps being fetched: '+' '.join(str(e) for e in bkg_steps))

        # Background dictionary from config
        background_dict = self.jedi_rendering.render_interface_model('background')

        # Get r2d2 dictionary
        r2d2_dict = self.jedi_rendering.render_interface_model('r2d2')

        # Loop over fc
        for fc in r2d2_dict['store']['fc']:

            # Reset target file
            target_file_template = os.path.split(background_dict['filename'])[1]

            # Datetime format to use
            user_date_format = fc['user_date_format']

            # Loop over file types
            for file_type in fc['file_type']:

                # Replace filetype in target_file_template
                target_file_type_template = target_file_template.replace("$(file_type)", file_type)

                # Looop over background steps
                for bkg_step in bkg_steps:

                    # Set the datetime format for the output files
                    background_time = forecast_start_time + isodate.parse_duration(bkg_step)
                    valid_time_str = background_time.strftime(user_date_format)

                    # Set the target file name
                    target_file = target_file_type_template.replace("$(valid_date)", valid_time_str)
                    target_file = os.path.join(self.cycle_dir(), target_file)

                    # Perform the store
                    store(date=forecast_start_time,
                          source_file=target_file,
                          model='geos',
                          file_type='bkg',
                          fc_date_rendering='analysis',
                          step=bkg_step,
                          resolution=self.config.horizontal_resolution(),
                          type='fc',
                          experiment=background_experiment)


# --------------------------------------------------------------------------------------------------


class StoreJdi(taskBase):

    def execute(self) -> None:
        """Store GEOS-CF NRT JDI background files in R2D2 as symlinks.

        The JDI collection contains 1-hourly instantaneous analysis files.
        Each calendar day has a single forecast run that initialises at 09Z,
        with hourly output steps PT0H (valid 09Z) through PT23H (valid 08Z
        the following day).

        For every hourly file valid on the cycle date this task resolves the
        source path from ``jdi_source_path`` (a template supporting ``YYYY``,
        ``MM``, ``DD``, ``HH`` placeholders), confirms the file exists, and
        calls ``r2d2.store`` with ``store_as_symlink=True`` so R2D2 registers
        a symlink rather than copying the data.

        Config keys (read from experiment YAML under the model component):

        - ``jdi_source_path``: path template, e.g.
          ``/css/gmao/geos-cf/NRTv2/priv/ana/YYYY/MM/DD/
          GEOS.cf.ana.jdi_inst_1hr_glo_C360x360x6_v72.YYYYMMDD_HHmmz.nc4``
        - ``jdi_experiment``: R2D2 experiment name (default ``geos_cf_v2``)
        - ``jdi_resolution``: R2D2 resolution string (default ``c360``)

        The Cylc cycle point must be the 09Z point for the day being ingested,
        e.g. ``2025-10-02T09:00:00Z``.
        """

        # Load R2D2 credentials
        load_r2d2_credentials(self.logger, self.platform())

        dry_run = self.config.dry_run(True)
        if dry_run:
            self.logger.info('DRY RUN MODE - No files will be stored')

        # Cycle time is the forecast initialisation time (always 09Z)
        forecast_start = dt.strptime(self.cycle_time(), datetime_formats['iso_format'])

        jdi_source_template = self.config.jdi_source_path()
        jdi_experiment = self.config.jdi_experiment('geos_cf_v2')
        jdi_resolution = self.config.jdi_resolution('c360')

        stored = 0
        skipped = 0

        # 24 hourly steps: PT0H (valid at forecast_start) through PT23H
        for hour_offset in range(24):
            valid_time = forecast_start + timedelta(hours=hour_offset)
            step = f'PT{hour_offset}H'

            source_file = self._resolve_jdi_path(jdi_source_template, valid_time)

            if not os.path.exists(source_file):
                self.logger.warning(f'JDI file not found, skipping: {source_file}')
                skipped += 1
                continue

            if dry_run:
                self.logger.info(
                    f'  [DRY RUN] Would store step={step}: {os.path.basename(source_file)}')
                stored += 1
                continue

            self.logger.info(f'  Storing step={step}: {os.path.basename(source_file)}')

            try:
                store(
                    model='geos_cf',
                    item='forecast',
                    step=step,
                    experiment=jdi_experiment,
                    resolution=jdi_resolution,
                    date=forecast_start.strftime('%Y%m%d_%H%Mz'),
                    source_file=source_file,
                    file_extension='nc4',
                    file_type='bkg',
                    store_as_symlink=True,
                )
            except PermissionError as exc:
                # R2D2 bug?: after creating the symlink, file_util._set_permissions
                # calls os.chmod which follows the symlink to the CSS source file.
                # Since we don't own that file, EPERM is raised, but the symlink
                # and DB entry are both created successfully before the chmod.
                # Need to verify the symlink points to the right file before continuing.
                r2d2_path = exc.filename
                if (r2d2_path
                        and os.path.islink(r2d2_path)
                        and os.readlink(r2d2_path) == source_file):
                    self.logger.warning(
                        f'  chmod on symlink target raised PermissionError (R2D2 bug) '
                        f'— symlink verified: {os.path.basename(r2d2_path)} -> '
                        f'{os.path.basename(source_file)}')
                else:
                    raise
            stored += 1

        verb = 'Would store' if dry_run else 'Stored'
        self.logger.info(f'JDI ingest complete: {verb} {stored} files, {skipped} skipped')

    # ------------------------------------------------------------------

    def _resolve_jdi_path(self, template: str, valid_time: dt) -> str:
        """Substitute placeholders in the JDI path template.

        Supports:
        - ``YDIR``, ``MDIR``, ``DDIR``: prefixed directory tokens (e.g. Y2025, M10, D02)
        - ``YYYYMMDD_HHmmz``: composite filename token (e.g. 20251002_0900z)
        - ``YYYY``, ``MM``, ``DD``, ``HH``: individual date/time tokens
        """
        return (template
                .replace('YDIR', 'Y' + valid_time.strftime('%Y'))
                .replace('MDIR', 'M' + valid_time.strftime('%m'))
                .replace('DDIR', 'D' + valid_time.strftime('%d'))
                .replace('YYYYMMDD_HHmmz', valid_time.strftime('%Y%m%d_%H%Mz'))
                .replace('YYYY', valid_time.strftime('%Y'))
                .replace('MM',   valid_time.strftime('%m'))
                .replace('DD',   valid_time.strftime('%d'))
                .replace('HH',   valid_time.strftime('%H')))
