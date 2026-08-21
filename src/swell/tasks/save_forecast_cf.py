# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import isodate
import os
from r2d2 import store


from swell.configuration.jedi.interfaces.geos_cf.model.r2d2 import forecast_filename, r2d2
from swell.tasks.base.task_base import taskBase
from swell.utilities.r2d2 import load_r2d2_credentials


# --------------------------------------------------------------------------------------------------


class SaveForecastCf(taskBase):

    def execute(self) -> None:

        """Store forecast files produced by the forecast task in R2D2

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """

        # Load R2D2 credentials
        # ---------------------
        load_r2d2_credentials(self.logger, self.platform())

        # Parse config
        # ------------
        window_length = self.config.window_length()
        forecast_length = self.config.forecast_length()
        forecast_output_frequency = self.config.forecast_output_frequency()
        expid = self.config.r2d2_experiment_id()
        fc_store = r2d2(self.jedi_rendering.__template_dict__)['store']['fc'][0]

        cycle_dir = self.cycle_dir()
        scratch_dir = os.path.join(cycle_dir, 'scratch')

        # Forecast starts at window begin
        # --------------------------------
        forecast_start = self.da_window_params.window_begin(window_length, dto=True)

        # Build list of forecast steps at PT1H frequency up to forecast_length
        # ----------------------------------------------------------------------
        forecast_length_dur = isodate.parse_duration(forecast_length)
        forecast_frequency_dur = isodate.parse_duration(forecast_output_frequency)

        step_dur = forecast_frequency_dur

        while step_dur <= forecast_length_dur:
            step = isodate.duration_isoformat(step_dur)

            file_time = forecast_start + step_dur
            fname = forecast_filename(file_time)
            source_file = os.path.join(scratch_dir, fname)
            if not os.path.isfile(source_file):
                self.logger.abort(f'Expected forecast file not found: {source_file}')

            self.logger.info(f'Storing {fname} at step {step}')

            store(
                model=fc_store['r2d2_model'],
                item='forecast',
                step=step,
                experiment=expid,
                resolution=self.config.horizontal_resolution(),
                date=forecast_start.strftime('%Y%m%dT%H%M%S%z'),
                source_file=source_file,
                file_extension='nc',
                file_type=fc_store['file_type'],
                store_as_symlink=False,
            )
            step_dur += forecast_frequency_dur
