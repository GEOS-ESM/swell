# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import tarfile

import r2d2

from swell.tasks.base.task_base import taskBase
from swell.utilities.r2d2 import load_r2d2_credentials

# --------------------------------------------------------------------------------------------------


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


class GetBackground(taskBase):
    """Fetch marine forecast archives from R2D2 and unpack them into the cycle directory.

    This task retrieves the pre-compressed marine background archives produced
    by the marine forecast save task and extracts them into the current cycle
    directory for downstream use.
    """

    def execute(self) -> None:
        """Retrieve the archived marine forecast outputs for the current cycle.

        The method loads the R2D2 credentials, resolves the active background
        time, fetches the archive for each configured marine model, and unpacks
        it into the cycle directory.
        """

        load_r2d2_credentials(
            self.logger,
            self.platform(),
            r2d2_server=self.config.r2d2_server(default=None),
        )

        r2d2_datastore = self.config.r2d2_datastore(default=None)
        marine_models = self.config.marine_models(None) or []
        window_type = self.config.window_type()
        window_length = self.config.window_length()
        horizontal_resolution = self.config.horizontal_resolution()

        local_background_time, local_background_time_dto = \
            self.da_window_params.local_background_time(window_length, window_type, dto=True)

        os.makedirs(self.cycle_dir(), 0o755, exist_ok=True)

        marine_model_configs = [('mom6', 'MOM.res')]
        if 'cice6' in marine_models:
            marine_model_configs.append(('cice6', 'cice.res'))

        for model_name, file_type in marine_model_configs:
            archive_path = _marine_archive_path(
                self.cycle_dir(), model_name, local_background_time)

            self.logger.info(
                f'Fetching marine background archive {os.path.basename(archive_path)} '
                f'({file_type}) for {model_name}'
            )

            fetch_kwargs = dict(
                item='forecast',
                target_file=archive_path,
                model=model_name,
                experiment=self.config.r2d2_experiment_id(),
                file_extension='tar.gz',
                resolution=horizontal_resolution,
                step='PT00',
                date=local_background_time_dto.strftime('%Y-%m-%d %H:%M:%S'),
                file_type=file_type,
            )
            if r2d2_datastore:
                fetch_kwargs['data_store'] = r2d2_datastore

            r2d2.fetch(**fetch_kwargs)

            if not os.path.exists(archive_path):
                self.logger.abort(f'Marine archive not fetched: {archive_path}')

            self.logger.info(f'Unpacking {os.path.basename(archive_path)} into {self.cycle_dir()}')
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(path=self.cycle_dir())

            os.remove(archive_path)
            self.logger.info(f'Unpacked {os.path.basename(archive_path)} into {self.cycle_dir()}')

# --------------------------------------------------------------------------------------------------
