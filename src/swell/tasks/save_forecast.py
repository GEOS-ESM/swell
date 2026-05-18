# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from datetime import datetime as dt
import isodate
import os
from r2d2 import store

from swell.tasks.base.task_base import taskBase
from swell.utilities.datetime_util import datetime_formats
from swell.utilities.r2d2 import load_r2d2_credentials


# --------------------------------------------------------------------------------------------------

class SaveForecast(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        """Store forecast files for a given experiment and cycle in R2D2.

           Dispatches to model-component- and window-type-specific store methods,
           mirroring the structure of LinkCoupledGeosOutput.

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """

        # Parse common configuration as instance variables
        # -------------------------------------------------
        self.marine_models = self.config.marine_models(None) or []
        self.window_type = self.config.window_type()
        self.window_length = self.config.window_length()
        self.window_begin_iso = self.da_window_params.window_begin_iso(self.window_length)
        self.background_experiment = self.experiment_id()
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
                if is_4d:
                    self._store_marine_4d(model_name, filename_key, file_type)
                else:
                    self._store_fc_dict(model_name, self.local_background_time_dto, step='PT0H')

        elif model_component == 'geos_cf':
            if is_4d:
                self.store_cf_4d()
            else:
                self.store_cf_3d()

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

        Parameters
        ----------
        model_name : str
            R2D2 model identifier (e.g. 'geos', 'mom6', 'cice6', 'geos_cf').
        bkg_dto : datetime
            Valid datetime of the forecast file (used directly as the r2d2 date).
        source_file : str
            Absolute path to the forecast file to store.
        file_type : str
            R2D2 file_type label (e.g. 'MOM.res', 'cice.res', 'bkg').
        step : str
            ISO 8601 duration string for the forecast step (e.g. 'PT0H', 'PT6H').
        """

        file_extension = file_type.split('.')[-1] if '.' in file_type else 'nc'

        self.logger.info(f'Storing {os.path.basename(source_file)} '
                         f'({file_type}) step={step} '
                         f'at {bkg_dto.strftime(datetime_formats["iso_format"])}')

        # store(
        #     item='forecast',
        #     model=model_name,
        #     experiment=self.background_experiment,
        #     resolution=self.horizontal_resolution,
        #     date=bkg_dto.strftime('%Y-%m-%d %H:%M:%S'),
        #     source_file=source_file,
        #     file_type=file_type,
        #     file_extension=file_extension,
        #     step=str(step),
        # )

    # ----------------------------------------------------------------------------------------------

    def _store_fc_dict(self, model_name: str, bkg_dto: dt, step: str) -> None:
        """Store all forecasts defined in r2d2_dict['store']['fc'] for one datetime.

        The filename for each entry is resolved by applying strftime to bkg_dto,
        ensuring it works for both static (marine, already strftime-compatible) and
        datetime-templated (atmosphere, cf) filename patterns.

        Parameters
        ----------
        model_name : str
            R2D2 model identifier.
        bkg_dto : datetime
            Valid datetime of the forecast — used as the r2d2 date and for filename resolution.
        step : str
            ISO 8601 duration string for the forecast step (e.g. 'PT0H', 'PT6H').
        """

        for fc in self.r2d2_dict['store']['fc']:
            if fc.get('r2d2_model') != model_name:
                continue
            file_type = fc['file_type']
            source_file = bkg_dto.strftime(fc['filename'])
            self._store_forecast(model_name, bkg_dto, source_file, file_type, step)

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

    def _store_marine_4d(self, model_name: str, filename_key: str, file_type: str) -> None:
        """Store marine forecasts across a 4D (or FGAT) window for one model component.

        Stores the window-begin forecast from r2d2_dict and then each subsequent
        state file from states_generator at its own exact valid datetime.

        Parameters
        ----------
        model_name : str
            R2D2 model identifier (e.g. 'mom6', 'cice6').
        filename_key : str
            Key in the states_generator dict for the source filename (e.g. 'ocn_filename').
        file_type : str
            R2D2 file_type label (e.g. 'MOM.res', 'cice.res').
        """

        # Store the window-begin forecast defined in the r2d2 dict (step = PT0H)
        self._store_fc_dict(model_name, self.local_background_time_dto, step='PT0H')

        # Store subsequent state forecasts from states_generator
        states = self.geos.states_generator(
            self.background_frequency, self.window_length,
            self.window_begin_iso, self.get_model(), self.marine_models)

        for state in states:
            state_dto = dt.strptime(state['date'], datetime_formats['iso_format'])
            step = isodate.duration_isoformat(state_dto - self.local_background_time_dto)
            source_file = os.path.join(self.cycle_dir(), state[filename_key])
            self._store_forecast(model_name, state_dto, source_file, file_type, step=step)

    # ----------------------------------------------------------------------------------------------
    # GEOS-CF store methods
    # ----------------------------------------------------------------------------------------------

    def store_cf_3d(self) -> None:
        """Store a single GEOS-CF forecast at the middle of a 3D window."""

        self.logger.abort('Storing a single GEOS-CF forecast at the middle of a 3D window is not ready yet.')

    # ----------------------------------------------------------------------------------------------

    def store_cf_4d(self) -> None:
        """Store GEOS-CF forecasts across a 4D (or FGAT) window.

        Uses states_generator to enumerate valid forecast datetimes.
        """
        self.logger.abort('Storing GEOS-CF forecasts across 4D window is not ready yet.')


# --------------------------------------------------------------------------------------------------
