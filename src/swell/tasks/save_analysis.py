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

class SaveAnalysis(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self) -> None:

        """Store analysis files for a given experiment and cycle in R2D2.

            Analysis files are handled differently then forecast files in R2D2, as they are stored
            at their exact valid time (the analysis time).

            Additionally, for 4D/FGAT windows, all analyses within the window are stored, each at its own valid time,
            rather than just the window-begin forecast as in the SaveForecast task.

            The marine FGAT only calculates one analysis and increment file per model (i.e., mom6 and cice6), 
            valid at the local background time.

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

        self.local_background_time, self.local_background_time_dto = self.da_window_params.local_background_time(
            self.window_length,
            self.window_type,
            dto=True)

        analysis_time_iso, analysis_time_dto = self.da_window_params.analysis_time_iso()

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
            marine_model_configs = [('mom6', 'ocn_filename', 'ocn.an')]
            if 'cice6' in self.marine_models:
                marine_model_configs.append(('cice6', 'ice_filename', 'ice.an'))

            for model_name, filename_key, file_type in marine_model_configs:
                self._store_an_dict(model_name, analysis_time_dto)

        else:
            self.logger.abort(f'Unknown model component for SaveAnalysis: {model_component}')

    # ----------------------------------------------------------------------------------------------

    def _store_analysis(self,
                        model_name: str,
                        ana_dto: dt,
                        source_file: str,
                        file_type: str,
                        ) -> None:
        """Call r2d2.store for a single analysis file at its exact valid time.

        Parameters
        ----------
        model_name : str
            R2D2 model identifier (e.g. 'geos', 'mom6', 'cice6', 'geos_cf').
        ana_dto : datetime
            Valid datetime of the analysis file (used directly as the r2d2 date).
        source_file : str
            Absolute path to the analysis file to store.
        file_type : str
            R2D2 file_type label (e.g. 'MOM.res', 'cice.res', 'bkg').
        """

        file_extension = file_type.split('.')[-1] if '.' in file_type else 'nc'

        self.logger.info(f'Storing {os.path.basename(source_file)} '
                         f'at {ana_dto.strftime(datetime_formats["iso_format"])}')

        # store(
        #     item='analysis',
        #     model=model_name,
        #     experiment=self.background_experiment,
        #     resolution=self.horizontal_resolution,
        #     date=ana_dto.strftime('%Y-%m-%d %H:%M:%S'),
        #     source_file=source_file,
        #     file_type=file_type,
        #     file_extension=file_extension,
        # )

    # ----------------------------------------------------------------------------------------------

    def _store_an_dict(self, model_name: str, ana_dto: dt) -> None:
        """Store all analyses defined in r2d2_dict['store']['an'] for one datetime.

        The filename for each entry is resolved by applying strftime to ana_dto,
        ensuring it works for both static (marine, already strftime-compatible) and
        datetime-templated (atmosphere) filename patterns.

        Parameters
        ----------
        model_name : str
            R2D2 model identifier.
        ana_dto : datetime
            Valid datetime of the analysis — used as the r2d2 date and for filename resolution.
        """

        for an in self.r2d2_dict['store']['an']:
            if an.get('r2d2_model') != model_name:
                continue
            file_type = an['file_type']
            source_file = ana_dto.strftime(an['filename'])
            self._store_analysis(model_name, ana_dto, source_file, file_type)

    # ----------------------------------------------------------------------------------------------
    # Atmosphere store methods (not implemeted yet, will need to resolve datetime-templated filenames for each analysis within the window)
    # ----------------------------------------------------------------------------------------------

    def store_atmosphere_3d(self) -> None:
        """Store a single atmospheric analysis at the middle of a 3D window."""

        self.logger.abort('Storing the window-begin atmospheric analysis is not ready yet.')

    # ----------------------------------------------------------------------------------------------

    def store_atmosphere_4d(self) -> None:
        """Store atmospheric analyses across a 4D (or FGAT) window.

        Uses states_generator to enumerate valid analysis datetimes and stores
        each file, keyed by its exact valid time.
        """

        self.logger.abort('Storing the window-begin atmospheric analysis is not ready yet.')

# --------------------------------------------------------------------------------------------------
