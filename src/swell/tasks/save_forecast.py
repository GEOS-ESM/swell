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
from swell.utilities.r2d2 import create_r2d2_config


# --------------------------------------------------------------------------------------------------


r2d2_model_dict = {
    'geos_atmosphere': 'geos',
    'geos_marine': 'mom6',
    'geos_cf': 'geos_cf',
}

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
        self.r2d2_local_path = self.config.r2d2_local_path()

        if self.window_type == '4D' or 'fgat' in self.suite_name():
            self.background_frequency = self.config.background_frequency()

        self.local_background_time, self.local_background_time_dto = self.da_window_params.local_background_time(
            self.window_length,
            self.window_type,
            dto=True)

        analysis_time_iso = self.da_window_params.analysis_time_iso()

        # Set R2D2 config file
        # --------------------
        create_r2d2_config(self.logger, self.platform(), self.cycle_dir(), self.r2d2_local_path)

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

        if self.window_type == '4D' or 'fgat' in self.suite_name():
            self.jedi_rendering.add_key('background_frequency', self.background_frequency)

        # Render r2d2 interface dict once, shared by all store methods
        # -------------------------------------------------------------
        self.r2d2_dict = self.jedi_rendering.render_interface_model('r2d2')

        # Dispatch to model- and window-type-specific store methods
        # ----------------------------------------------------------
        model_component = self.get_model()

        if model_component == 'geos_atmosphere':
            if self.window_type == '4D' or 'fgat' in self.suite_name():
                self.store_atmosphere_4d()
            else:
                self.store_atmosphere_3d()

        elif model_component == 'geos_marine':
            if self.window_type == '4D' or 'fgat' in self.suite_name():
                self.store_mom6_4d()
                if 'cice6' in self.marine_models:
                    self.store_cice6_4d()
            else:
                self.store_mom6_3d()
                if 'cice6' in self.marine_models:
                    self.store_cice6_3d()

        elif model_component == 'geos_cf':
            if self.window_type == '4D' or 'fgat' in self.suite_name():
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
    # Marine (MOM6) store methods
    # ----------------------------------------------------------------------------------------------

    def store_mom6_3d(self) -> None:
        """Store a single MOM6 ocean forecast at the middle of a 3D window."""

        self._store_fc_dict(r2d2_model_dict['geos_marine'], self.local_background_time_dto, step='PT0H')

    # ----------------------------------------------------------------------------------------------

    def store_mom6_4d(self) -> None:
        """Store MOM6 ocean forecasts across a 4D (or FGAT) window.

        Stores the window-begin forecast (from r2d2_dict['store']['fc']) and then
        each subsequent state file enumerated by states_generator, each at its own
        exact valid datetime.
        """

        # Store the window-begin forecast defined in the r2d2 dict (step = PT0H)
        self._store_fc_dict(r2d2_model_dict['geos_marine'], self.local_background_time_dto, step='PT0H')

        # Store subsequent state forecasts from states_generator
        # ocn_filename format: "ocn.fc.<window_begin_iso>.<step>.nc" — step embedded in filename
        states = self.geos.states_generator(
            self.background_frequency, self.window_length,
            self.window_begin_iso, self.get_model(), self.marine_models)

        for state in states:
            state_dto = dt.strptime(state['date'], datetime_formats['iso_format'])
            step = isodate.duration_isoformat(state_dto - self.local_background_time_dto)
            source_file = os.path.join(self.cycle_dir(), state['ocn_filename'])
            self._store_forecast(r2d2_model_dict['geos_marine'], state_dto,
                                  source_file, 'MOM.res', step=step)

    # ----------------------------------------------------------------------------------------------
    # Marine (CICE6) store methods
    # ----------------------------------------------------------------------------------------------

    def store_cice6_3d(self) -> None:
        """Store a single CICE6 sea-ice forecast at the middle of a 3D window."""

        self._store_fc_dict('cice6', self.local_background_time_dto, step='PT0H')

    # ----------------------------------------------------------------------------------------------

    def store_cice6_4d(self) -> None:
        """Store CICE6 sea-ice forecasts across a 4D (or FGAT) window.

        Mirrors store_mom6_4d: stores the window-begin forecast from r2d2_dict and
        then each subsequent state file from states_generator at its own valid datetime.
        """

        # Store the window-begin forecast defined in the r2d2 dict (step = PT0H)
        self._store_fc_dict('cice6', self.local_background_time_dto, step='PT0H')

        # Store subsequent state forecasts from states_generator
        # ice_filename format: "ice.fc.<window_begin_iso>.<step>.nc" — step embedded in filename
        states = self.geos.states_generator(
            self.background_frequency, self.window_length,
            self.window_begin_iso, self.get_model(), self.marine_models)

        for state in states:
            state_dto = dt.strptime(state['date'], datetime_formats['iso_format'])
            step = isodate.duration_isoformat(state_dto - self.local_background_time_dto)
            source_file = os.path.join(self.cycle_dir(), state['ice_filename'])
            self._store_forecast('cice6', state_dto, source_file, 'cice.res', step=step)

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
