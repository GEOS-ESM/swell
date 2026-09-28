# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from datetime import datetime as dt
import os
import tarfile

from swell.tasks.base.task_base import taskBase
from swell.utilities.compress import compress_file

# --------------------------------------------------------------------------------------------------

"""Create compressed marine forecast archives for GEOS marine components."""


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


class RunCompressForecast(taskBase):
    """Compress marine state files into a tar.gz archive for later storage.

    The task runs on a compute node so that pigz parallelism is available.
    """

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:
        """Gather marine states for the active cycle and create per-model archives.

        The method resolves the background window parameters, prepares the
        interface rendering data, and compresses each requested marine model's
        state files into a tar.gz archive.
        """

        marine_models = self.config.marine_models(None) or []
        window_type = self.config.window_type()
        window_length = self.config.window_length()
        window_begin_iso = self.da_window_params.window_begin_iso(window_length)
        horizontal_resolution = self.config.horizontal_resolution()

        is_4d = window_type == '4D' or 'fgat' in self.suite_name()

        if is_4d:
            background_frequency = self.config.background_frequency()

        (local_background_time, local_background_time_dto) = \
            self.da_window_params.local_background_time(window_length, window_type, dto=True)

        analysis_time_iso = self.da_window_params.analysis_time_iso()
        local_background_time_iso = self.da_window_params.local_background_time_iso(
            window_length, window_type)

        self.jedi_rendering.add_key('local_background_time', local_background_time)
        self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)
        self.jedi_rendering.add_key('marine_models', marine_models)
        self.jedi_rendering.add_key('horizontal_resolution', horizontal_resolution)
        self.jedi_rendering.add_key('analysis_time_iso', analysis_time_iso)

        if is_4d:
            self.jedi_rendering.add_key('background_frequency', background_frequency)

        r2d2_dict = self.jedi_rendering.render_interface_model('r2d2')

        marine_model_configs = [('mom6', 'ocn_filename', 'MOM.res')]
        if 'cice6' in marine_models:
            marine_model_configs.append(('cice6', 'ice_filename', 'cice.res'))

        for model_name, filename_key, _ in marine_model_configs:
            self._compress_marine(
                model_name=model_name,
                filename_key=filename_key,
                is_4d=is_4d,
                background_frequency=background_frequency if is_4d else None,
                window_length=window_length,
                window_begin_iso=window_begin_iso,
                marine_models=marine_models,
                r2d2_dict=r2d2_dict,
                local_background_time=local_background_time,
                local_background_time_dto=local_background_time_dto,
            )

    # ----------------------------------------------------------------------------------------------

    def _compress_marine(self,
                         model_name: str,
                         filename_key: str,
                         is_4d: bool,
                         background_frequency,
                         window_length: str,
                         window_begin_iso: str,
                         marine_models: list,
                         r2d2_dict: dict,
                         local_background_time: str,
                         local_background_time_dto: dt,
                         ) -> None:
        """Create and compress the archive for a single marine model.

        Args:
            model_name: Marine model identifier.
            filename_key: Configuration key used to locate state files.
            is_4d: Whether the current window is a 4D or FGAT-style window.
            background_frequency: Frequency used to discover background states.
            window_length: DA window length string.
            window_begin_iso: ISO-formatted start of the DA window.
            marine_models: List of configured marine models.
            r2d2_dict: Rendered interface model data for R2D2 file discovery.
            local_background_time: Local background time string.
            local_background_time_dto: Parsed local background datetime.
        """

        # Gather file paths
        files_to_archive = []

        for fc in r2d2_dict['store']['fc']:
            if fc.get('r2d2_model') == model_name:
                source_file = local_background_time_dto.strftime(fc['filename'])
                files_to_archive.append(source_file)

        if is_4d:
            states = self.geos.states_generator(
                background_frequency, window_length,
                window_begin_iso, self.get_model(), marine_models)
            for state in states:
                files_to_archive.append(os.path.join(self.cycle_dir(), state[filename_key]))

        for f in files_to_archive:
            if not os.path.exists(f):
                if os.path.islink(f):
                    self.logger.abort(f"Marine state is a broken symbolic link: {f}")
                else:
                    self.logger.abort(f"Required marine state file does not exist: {f}")

        archive_gz = _marine_archive_path(self.cycle_dir(), model_name, local_background_time)
        archive_tar = archive_gz[:-3]  # strip '.gz'

        self.logger.info(f"Archiving {len(files_to_archive)} marine state file(s) into "
                         f"{archive_gz}")
        self.logger.debug(f"Files to archive: {files_to_archive}")

        try:
            with tarfile.open(archive_tar, 'w', dereference=True) as tar:
                for f in files_to_archive:
                    tar.add(f, arcname=os.path.basename(f))
        except Exception as e:
            self.logger.abort(f"Failed to create tar archive for marine states: {e}")

        try:
            compress_file(archive_tar, algorithm='pigz')
        except Exception as e:
            self.logger.abort(f"Failed to compress marine archive with pigz: {e}")

        os.remove(archive_tar)


# ----------------------------------------------------------------------------------------------
