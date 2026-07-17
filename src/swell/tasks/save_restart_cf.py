# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import isodate
import os
from r2d2 import store

from swell.tasks.base.task_base import taskBase
from swell.utilities.compress import compress_file, compressed_extension
from swell.utilities.r2d2 import load_r2d2_credentials

# --------------------------------------------------------------------------------------------------


class SaveRestartCf(taskBase):

    def execute(self):

        """
        Store GEOS-CF checkpoint restart files to R2D2 as symlinks or actual files.
        Saves checkpoint files that are valid at the beginning of the next DA window so they
        can be retrieved by GetRestartCf in the subsequent cycle.
        """

        model = self.__model__

        # Load R2D2 credentials
        # ---------------------
        load_r2d2_credentials(self.logger, self.platform())

        # Parse config
        # ------------
        window_length = self.config.window_length()
        expid = self.config.r2d2_experiment_id()
        horizontal_resolution = self.config.horizontal_resolution()

        cycle_dir = self.cycle_dir()
        scratch_dir = os.path.join(cycle_dir, 'scratch')

        # Window begin for the current cycle
        # ------------------------------------
        window_begin = self.da_window_params.window_begin(window_length, dto=True)

        # Checkpoint files are valid at the start of the next window
        # -----------------------------------------------------------
        next_window_begin = window_begin + isodate.parse_duration(window_length)
        checkpoint_time_str = next_window_begin.strftime('%Y%m%d_%H%Mz')

        rst_file_types = self.config.rst_file_types()
        rst_store_interval = self.config.rst_store_interval(None)

        compress_output = self.config.compress_output(False)
        compress_algorithm = self.config.compress_algorithm('gzip')
        compress_pigz_threads = self.config.compress_pigz_threads(4)

        # Determine whether to store as a symlink for this cycle
        # --------------------------------------------------------
        store_as_symlink = True
        if rst_store_interval is not None:
            cycle_duration = isodate.parse_duration(window_length)
            elapsed = window_begin - self.start_cycle_point_dto()
            cycle_number = round(elapsed / cycle_duration) + 1
            store_as_symlink = (cycle_number % rst_store_interval != 0)
            self.logger.info(f'Cycle number: {cycle_number}, rst_store_interval: '
                             f'{rst_store_interval}, store_as_symlink: {store_as_symlink}')

        for file_type in rst_file_types:
            fname = f'{file_type}_checkpoint.{checkpoint_time_str}.nc4'
            source_file = os.path.join(scratch_dir, fname)

            if not os.path.isfile(source_file):
                self.logger.abort(f'Expected checkpoint file not found: {source_file}')

            self.logger.info(f'Storing {fname}')

            actual_source = source_file
            actual_extension = 'nc'
            compressed_path = None

            if compress_output:
                if store_as_symlink:
                    self.logger.warning(
                        f'compress_output=True and store_as_symlink=True are incompatible. '
                        f'Forcing store_as_symlink=False for {fname}.'
                    )
                    store_as_symlink = False

                self.logger.info(
                    f'Compressing {source_file} using {compress_algorithm}'
                    + (f' ({compress_pigz_threads} threads)'
                       if compress_algorithm == 'pigz' else '')
                )
                compressed_path = compress_file(
                    source_file,
                    algorithm=compress_algorithm,
                    num_threads=compress_pigz_threads,
                )
                actual_source = compressed_path
                actual_extension = compressed_extension('nc')
                self.logger.info(
                    f'Compressed {source_file} -> {compressed_path} '
                    f'(extension: {actual_extension})'
                )

            try:
                store(
                    model=model,
                    item='forecast',
                    step=window_length,
                    experiment=expid,
                    resolution=horizontal_resolution,
                    date=window_begin.strftime('%Y%m%dT%H%M%S%z'),
                    source_file=actual_source,
                    file_extension=actual_extension,
                    file_type=file_type,
                    store_as_symlink=store_as_symlink,
                )
            finally:
                if compressed_path is not None and os.path.exists(compressed_path):
                    os.remove(compressed_path)

# --------------------------------------------------------------------------------------------------
