# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from datetime import datetime as dt
from datetime import timedelta
import os
from r2d2 import store

from swell.tasks.base.task_base import taskBase
from swell.utilities.datetime_util import datetime_formats
from swell.utilities.r2d2 import load_r2d2_credentials

# --------------------------------------------------------------------------------------------------


class IngestCFBackground(taskBase):

    def execute(self) -> None:
        """Ingest GEOS-CF NRT JDI background files into R2D2 as symlinks.

        The JDI collection contains 1-hourly instantaneous analysis files.
        Each calendar day has a single forecast run that initialises at 09Z,
        with hourly output steps PT0H (valid 09Z) through PT23H (valid 08Z
        the following day).

        For every hourly file valid on the cycle date this task resolves the
        source path by calling ``strftime`` on ``background_source_path``,
        confirms the file exists, and calls ``r2d2.store`` with
        ``store_as_symlink=True`` so R2D2 registers a symlink rather than
        copying the data.

        Config keys (read from experiment YAML under the model component):

        - ``background_source_path``: strftime path template, e.g.
          ``/css/gmao/geos-cf/NRTv2/priv/ana/Y%Y/M%m/D%d/
          GEOS.cf.ana.jdi_inst_1hr_glo_C360x360x6_v72.%Y%m%d_%H%Mz.R0.nc4``
        - ``background_experiment``: R2D2 experiment name (default ``geos_cf_v2``)
        - ``horizontal_resolution``: R2D2 resolution string (default ``c360``)

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

        source_template = self.config.background_source_path()
        experiment = self.config.background_experiment('geos_cf_v2')
        resolution = self.config.horizontal_resolution('c360')

        stored = 0
        skipped = 0

        # 24 hourly steps: PT0H (valid at forecast_start) through PT23H
        for hour_offset in range(24):
            valid_time = forecast_start + timedelta(hours=hour_offset)
            step = f'PT{hour_offset}H'

            source_file = valid_time.strftime(source_template)

            if not os.path.exists(source_file):
                self.logger.warning(f'Background file not found, skipping: {source_file}')
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
                    experiment=experiment,
                    resolution=resolution,
                    date=forecast_start.strftime('%Y%m%d_%H%Mz'),
                    source_file=source_file,
                    file_extension='nc4',
                    file_type='bkg',
                    store_as_symlink=True,
                )
            except PermissionError as exc:
                # R2D2 bug: after creating the symlink, file_util._set_permissions
                # calls os.chmod which follows the symlink to the CSS source file.
                # Since we don't own that file, EPERM is raised, but the symlink
                # and DB entry are both created successfully before the chmod.
                # Verify the symlink points to the right file before continuing.
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
        self.logger.info(f'CF background ingest complete: {verb} {stored} files, {skipped} skipped')
