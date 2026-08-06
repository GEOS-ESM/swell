# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from datetime import datetime as dt
import isodate
import os
import tarfile
from r2d2 import store

from swell.deployment.platforms.platforms import login_or_compute
from swell.tasks.base.task_base import taskBase
from swell.utilities.compress import compress_file
from swell.utilities.datetime_util import datetime_formats
from swell.utilities.r2d2 import load_r2d2_credentials


# --------------------------------------------------------------------------------------------------

class SaveForecast(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        """Store forecast files for a given experiment and cycle in R2D2.

        Note:
            All inputs are extracted from the JEDI experiment file configuration.
            See the taskBase constructor for more information.
        """

        # Parse common configuration as instance variables
        # -------------------------------------------------
        self.marine_models = self.config.marine_models(None) or []
        self.window_type = self.config.window_type()
        self.window_length = self.config.window_length()
        self.window_begin_iso = self.da_window_params.window_begin_iso(self.window_length)
        self.horizontal_resolution = self.config.horizontal_resolution()

        # Load R2D2 credentials
        # ---------------------
        load_r2d2_credentials(self.logger, self.platform())

        is_4d = self.window_type == '4D' or 'fgat' in self.suite_name()

        if is_4d:
            self.background_frequency = self.config.background_frequency()

        self.local_background_time, self.local_background_time_dto = self.da_window_params.local_background_time(
            self.window_length,
            self.window_type,
            dto=True)

        # Compute the step that aligns with GetBackground's fetch key
        window_length_dur = isodate.parse_duration(self.window_length)
        window_offset_dur = self.da_window_params.window_offset(self.window_length, dto=True)
        self.marine_step = isodate.duration_isoformat(window_length_dur - window_offset_dur)

        analysis_time_iso = self.da_window_params.analysis_time_iso()

        # Populate jedi_rendering template dictionary before rendering
        # (mirrors run_jedi_variational_executable.py)
        # ------------------------------------------------------------
        local_background_time_iso = self.da_window_params.local_background_time_iso(
            self.window_length, self.window_type)

        self.jedi_rendering.add_key('local_background_time', self.local_background_time)
        self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)
        self.jedi_rendering.add_key('marine_models', self.marine_models)
        self.jedi_rendering.add_key('horizontal_resolution', self.horizontal_resolution)
        self.jedi_rendering.add_key('analysis_time_iso', analysis_time_iso)

        if is_4d:
            self.jedi_rendering.add_key('background_frequency', self.background_frequency)

        # Render r2d2 interface dict once, shared by all store methods
        # -------------------------------------------------------------
        self.r2d2_dict = self.jedi_rendering.render_interface_model('r2d2')

        # Dispatch to model- and window-type-specific store methods
        # ----------------------------------------------------------
        model_component = self.get_model()

        if model_component == 'geos_atmosphere':
            if is_4d:
                self.store_atmosphere_4d()
            else:
                self.store_atmosphere_3d()

        elif model_component == 'geos_marine':
            marine_model_configs = [('mom6', 'ocn_filename', 'MOM.res')]
            if 'cice6' in self.marine_models:
                marine_model_configs.append(('cice6', 'ice_filename', 'cice.res'))

            for model_name, filename_key, file_type in marine_model_configs:
                self._store_compressed_marine(model_name, filename_key, file_type, is_4d,
                                              self.marine_step)

        else:
            self.logger.abort(f'Unknown model component for SaveForecast: {model_component}')

    # ----------------------------------------------------------------------------------------------

    def _store_forecast(self,
                        model_name: str,
                        bkg_dto: dt,
                        source_file: str,
                        file_type: str,
                        step: str,
                        ) -> None:
        """Call r2d2.store for a single forecast file at its exact valid time.

        Args:
            model_name (str): R2D2 model identifier (e.g. 'geos', 'mom6', 'cice6', 'geos_cf').
            bkg_dto (dt): Valid datetime of the forecast file (used directly as the r2d2 date).
            source_file (str): Absolute path to the forecast file to store.
            file_type (str): R2D2 file_type label (e.g. 'MOM.res', 'cice.res', 'bkg').
            step (str): ISO 8601 duration string for the forecast step (e.g. 'PT0H', 'PT6H').
        """

        if source_file.endswith('.tar.gz'):
            file_extension = 'tar.gz'
        else:
            file_extension = source_file.split('.')[-1] if '.' in source_file else 'nc'

        self.logger.info(f'Storing {os.path.basename(source_file)} '
                         f'({file_type}) step={step} '
                         f'at {bkg_dto.strftime(datetime_formats["iso_format"])}')

        store(
            item='forecast',
            model=model_name,
            experiment=self.config.r2d2_experiment_id(),
            resolution=self.horizontal_resolution,
            date=bkg_dto.strftime('%Y-%m-%d %H:%M:%S'),
            source_file=source_file,
            file_type=file_type,
            file_extension=file_extension,
            step=str(step),
        )

    # ----------------------------------------------------------------------------------------------
    # Atmosphere store methods
    # ----------------------------------------------------------------------------------------------

    def store_atmosphere_3d(self) -> None:
        """Store a single atmospheric forecast at the middle of a 3D window."""

        self.logger.abort('Storing the window-begin atmospheric forecast is not ready yet.')

    # ----------------------------------------------------------------------------------------------

    def store_atmosphere_4d(self) -> None:
        """Store atmospheric forecasts across a 4D (or FGAT) window.

        Uses states_generator to enumerate valid forecast datetimes and stores
        each file, keyed by its exact valid time.
        """

        self.logger.abort('Storing the window-begin atmospheric forecast is not ready yet.')

    # ----------------------------------------------------------------------------------------------
    # Marine store methods
    # ----------------------------------------------------------------------------------------------

    def _store_compressed_marine(self,
                                 model_name: str,
                                 filename_key: str,
                                 file_type: str,
                                 is_4d: bool,
                                 step: str,
                                 ) -> None:
        """Collect all marine state files, check that they exist, compress them with gz,
        and store the compressed archive in R2D2.

        Args:
            model_name (str): R2D2 model identifier (e.g. 'mom6', 'cice6').
            filename_key (str): Key in the states_generator dict for the source filename
                (e.g. 'ocn_filename', 'ice_filename').
            file_type (str): R2D2 file_type label (e.g. 'MOM.res', 'cice.res').
            is_4d (bool): Whether the model is running in 4D (or FGAT) mode.
            step (str): ISO 8601 duration for the R2D2 forecast step key.
        """

        # Gather file paths
        files_to_compress = []

        # 1. Window-begin forecast files (from r2d2_dict)
        for fc in self.r2d2_dict['store']['fc']:
            if fc.get('r2d2_model') == model_name:
                source_file = self.local_background_time_dto.strftime(fc['filename'])
                files_to_compress.append(source_file)

        # 2. Subsequent state forecasts (for 4D)
        if is_4d:
            states = self.geos.states_generator(
                self.background_frequency, self.window_length,
                self.window_begin_iso, self.get_model(), self.marine_models)

            for state in states:
                source_file = os.path.join(self.cycle_dir(), state[filename_key])
                files_to_compress.append(source_file)

        # Step 1: Check if all marine states exist
        for f in files_to_compress:
            if not os.path.exists(f):
                if os.path.islink(f):
                    self.logger.abort(f"Marine state is a broken symbolic link: {f}")
                else:
                    self.logger.abort(f"Required marine state file does not exist: {f}")

        # Step 2a: Create an uncompressed tar archive
        archive_tar = os.path.join(self.cycle_dir(),
                                   f"{model_name}.{self.local_background_time}.tar")
        archive_path = archive_tar + '.gz'

        self.logger.info(f"Archiving {len(files_to_compress)} marine state file(s) into "
                         f"{archive_path}")
        self.logger.debug(f"Files to archive: {files_to_compress}")

        try:
            with tarfile.open(archive_tar, 'w', dereference=True) as tar:
                for f in files_to_compress:
                    tar.add(f, arcname=os.path.basename(f))
        except Exception as e:
            self.logger.abort(f"Failed to create tar archive for marine states: {e}")

        # Step 2b: Compress — pigz on compute nodes, stdlib gzip on login nodes
        algorithm = 'pigz' if login_or_compute(self.platform()) == 'compute' else 'gzip'
        self.logger.info(f"Compressing archive using {algorithm}")
        try:
            compress_file(archive_tar, algorithm=algorithm)
        except Exception as e:
            self.logger.abort(f"Failed to compress marine archive with {algorithm}: {e}")
        os.remove(archive_tar)

        # Step 3: Store in R2D2
        self._store_forecast(
            model_name=model_name,
            bkg_dto=self.local_background_time_dto,
            source_file=archive_path,
            file_type=file_type,
            step=step,
        )

# --------------------------------------------------------------------------------------------------
