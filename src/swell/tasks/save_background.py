# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from datetime import datetime as dt
from datetime import timedelta
import os
import shutil
from r2d2 import store

from swell.tasks.base.task_base import taskBase
from swell.utilities.compress import compress_file, compressed_extension
from swell.utilities.datetime_util import datetime_formats
from swell.utilities.r2d2 import load_r2d2_credentials

# --------------------------------------------------------------------------------------------------


class SaveBackground(taskBase):

    def execute(self) -> None:
        """Ingest NRT background files into R2D2 as symlinks.

        Designed for collections where background files already exist on a
        shared filesystem and only need to be registered in R2D2 via symlinks
        rather than copied. Currently used for the GEOS-CF JDI collection.

        The collection contains 1-hourly instantaneous analysis files with a
        single forecast run initializing at 09Z each day. Steps PT0H (valid
        09Z) through PT23H (valid 08Z the following day) are ingested.

        For every hourly step the source path is resolved by calling
        ``strftime`` on ``background_source_path``, the file is confirmed to
        exist, and ``r2d2.store`` is called with ``store_as_symlink=True``.

        Config keys (read from experiment YAML under the model component):

        - ``background_source_path``: strftime path template, e.g.
          ``/css/gmao/geos-cf/NRTv2/priv/ana/Y%Y/M%m/D%d/
          GEOS.cf.ana.jdi_inst_1hr_glo_C360x360x6_v72.%Y%m%d_%H%Mz.R0.nc4``
        - ``background_experiment``: R2D2 experiment name (default ``geos_cf_oper``)
        - ``horizontal_resolution``: R2D2 resolution string (default ``c360``)
        - ``store_as_symlink``: if ``True`` (default), register files as symlinks
          in R2D2 rather than copying them
        - ``compress_output``: if ``True`` (default ``False``), gzip/pigz-compress
          each file before storing to save R2D2 disk space. Incompatible with
          ``store_as_symlink`` (the compressed copy is not the original file), so
          ``store_as_symlink`` is forced to ``False`` when compression is enabled.
        - ``compress_algorithm``: ``gzip`` (default) or ``pigz`` (parallel, requires
          the ``pigz`` binary on ``PATH``)
        - ``compress_pigz_threads``: thread count for ``pigz`` (default 4)

        The Cylc cycle point must be the forecast initialization time,
        e.g. ``2025-10-02T09:00:00Z``.
        """

        # Load R2D2 credentials
        load_r2d2_credentials(self.logger, self.platform())

        dry_run = self.config.dry_run(True)
        if dry_run:
            self.logger.info('DRY RUN MODE - No files will be stored')

        # Cycle time is the forecast initialization time
        forecast_start = dt.strptime(self.cycle_time(), datetime_formats['iso_format'])

        # This suite is built around a single 09Z forecast run. If cycle_times
        # is accidentally changed the step offsets (PT0H–PT23H) will be wrong.
        if forecast_start.hour != 9:
            self.logger.abort(
                f'SaveBackground expects cycle_time hour to be 09Z, '
                f'got {forecast_start.hour:02d}Z. '
                f'Ensure cycle_times is set to [T09] in the suite config.'
            )

        model = self.get_model()
        source_template = self.config.background_source_path()
        experiment = self.config.background_experiment('geos_cf_oper')
        resolution = self.config.horizontal_resolution('c360')
        store_as_symlink = self.config.store_as_symlink(True)

        compress_output = self.config.compress_output(False)
        compress_algorithm = self.config.compress_algorithm('gzip')
        compress_pigz_threads = self.config.compress_pigz_threads(4)

        if compress_output and store_as_symlink:
            self.logger.warning(
                'compress_output=True and store_as_symlink=True are incompatible '
                '(a compressed copy is not the original file). '
                'Forcing store_as_symlink=False.'
            )
            store_as_symlink = False

        if compress_output:
            os.makedirs(self.cycle_dir(), 0o755, exist_ok=True)

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

            store_source = source_file
            store_extension = 'nc4'
            staged_compressed_file = None

            if compress_output:
                # Source files live on a shared, often read-only NRT filesystem —
                # stage a local copy in the cycle directory before compressing
                # rather than writing next to the original.
                staged_file = os.path.join(self.cycle_dir(), os.path.basename(source_file))
                try:
                    shutil.copy(source_file, staged_file)
                    staged_compressed_file = compress_file(
                        staged_file,
                        algorithm=compress_algorithm,
                        num_threads=compress_pigz_threads,
                    )
                except Exception as exc:
                    self.logger.abort(
                        f'Failed to compress background file {source_file}: {exc}')
                finally:
                    if os.path.exists(staged_file):
                        os.remove(staged_file)

                store_source = staged_compressed_file
                store_extension = compressed_extension('nc4')

            try:
                store(
                    model=model,
                    item='forecast',
                    step=step,
                    experiment=experiment,
                    resolution=resolution,
                    date=forecast_start.strftime('%Y%m%d_%H%Mz'),
                    source_file=store_source,
                    file_extension=store_extension,
                    file_type='bkg',
                    store_as_symlink=store_as_symlink,
                )
            except PermissionError as exc:
                # R2D2 bug: after creating the symlink, file_util._set_permissions
                # calls os.chmod which follows the symlink to the source file on
                # the shared filesystem. Since we don't own that file, EPERM is
                # raised, but the symlink and DB entry are both created successfully
                # before the chmod. Verify the symlink before continuing.
                # Only applies when store_as_symlink=True; a real copy never hits this.
                r2d2_path = exc.filename
                if (store_as_symlink
                        and r2d2_path
                        and os.path.islink(r2d2_path)
                        and os.readlink(r2d2_path) == source_file):
                    self.logger.warning(
                        f'  chmod on symlink target raised PermissionError (R2D2 bug) '
                        f'— symlink verified: {os.path.basename(r2d2_path)} -> '
                        f'{os.path.basename(source_file)}')
                else:
                    raise
            finally:
                if staged_compressed_file and os.path.exists(staged_compressed_file):
                    os.remove(staged_compressed_file)
            stored += 1

        verb = 'Would store' if dry_run else 'Stored'
        self.logger.info(f'Background ingest complete: {verb} {stored} files, {skipped} skipped')
