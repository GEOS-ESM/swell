# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
from r2d2 import store

from swell.tasks.base.task_base import taskBase
from swell.utilities.datetime_util import datetime_formats
from swell.utilities.r2d2 import load_r2d2_credentials


# --------------------------------------------------------------------------------------------------

"""Store pre-compressed marine forecast archives in R2D2."""


def _marine_archive_path(cycle_dir: str, model_name: str, local_background_time: str) -> str:
    """Return the canonical path for a marine background tar.gz archive.

    Args:
        cycle_dir: Directory where the cycle artifacts are written.
        model_name: Name of the marine model, such as "mom6" or "cice6".
        local_background_time: Background time string used in the archive name.

    Returns:
        The full path to the expected archive file.
    """
    return os.path.join(cycle_dir, f"{model_name}.{local_background_time}.tar.gz")

# --------------------------------------------------------------------------------------------------


class SaveForecast(taskBase):
    """Store the pre-compressed marine archive in R2D2.

    The task runs on a login node, where internet access is available for
    R2D2. The archive must have been produced by RunCompressForecast in the
    same cycle.
    """

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:
        """Resolve the target background time and store the generated archives.

        The method loads the R2D2 credentials, determines the active window
        parameters, and uploads each marine model archive that was produced in
        the current cycle.

        The archive files are stored at background time, which changes according to the configured
        window type (and/or suite type) and length.
        """

        self.marine_models = self.config.marine_models(None) or []
        window_type = self.config.window_type()
        self.window_length = self.config.window_length()
        self.horizontal_resolution = self.config.horizontal_resolution()

        load_r2d2_credentials(self.logger, self.platform())

        self.local_background_time, self.local_background_time_dto = \
            self.da_window_params.local_background_time(self.window_length, window_type, dto=True)

        marine_model_configs = [('mom6', 'MOM.res')]
        if 'cice6' in self.marine_models:
            marine_model_configs.append(('cice6', 'cice.res'))

        for model_name, file_type in marine_model_configs:
            self._store_forecast(model_name, file_type)

    # ----------------------------------------------------------------------------------------------

    def _store_forecast(self, model_name: str, file_type: str) -> None:
        """Upload a single marine archive to R2D2.

        Args:
            model_name: Marine model identifier.
            file_type: File type label used when storing the archive.
        """

        archive_path = _marine_archive_path(
            self.cycle_dir(), model_name, self.local_background_time)

        if not os.path.exists(archive_path):
            self.logger.abort(
                f"Marine archive not found (did RunCompressForecast complete?): {archive_path}")

        self.logger.info(
            f'Storing {os.path.basename(archive_path)} ({file_type}) '
            f'step=PT00 '
            f'at {self.local_background_time_dto.strftime(datetime_formats["iso_format"])}')

        store(
            item='forecast',
            model=model_name,
            experiment=self.config.r2d2_experiment_id(),
            resolution=self.horizontal_resolution,
            date=self.local_background_time_dto.strftime('%Y-%m-%d %H:%M:%S'),
            source_file=archive_path,
            file_type=file_type,
            file_extension='tar.gz',
            step='PT00',
            store_as_symlink=False,
        )

# --------------------------------------------------------------------------------------------------
