# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import isodate
import os

import swell.configuration.question_defaults as qd
from swell.tasks.base.task_base import taskBase
from swell.tasks.base.task_setup import TaskSetup
from swell.tasks.base.task_attributes import task_attributes
from swell.utilities.r2d2_utils import load_r2d2_credentials

# --------------------------------------------------------------------------------------------------

task_name = 'SaveRestartCf'


@task_attributes.register(task_name)
class Setup(TaskSetup):
    def set_defaults(self):
        self.base_name = task_name
        self.is_cycling = True
        self.model_dep = True
        self.questions = [
            qd.window_length(),
            qd.horizontal_resolution(),
            qd.rst_file_types(),
            qd.rst_store_interval(),
        ]

# --------------------------------------------------------------------------------------------------


class SaveRestartCf(taskBase):

    def execute(self):

        """
        Store GEOS-CF checkpoint restart files to R2D2 as symlinks or actual files.
        Saves checkpoint files that are valid at the beginning of the next DA window so they
        can be retrieved by GetRestartCf in the subsequent cycle.
        """

        from r2d2 import store

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

            store(
                model=model,
                item='forecast',
                step=window_length,
                experiment=expid,
                resolution=horizontal_resolution,
                date=window_begin.strftime('%Y%m%dT%H%M%S%z'),
                source_file=source_file,
                file_extension='nc',
                file_type=file_type,
                store_as_symlink=store_as_symlink,
            )

# --------------------------------------------------------------------------------------------------
