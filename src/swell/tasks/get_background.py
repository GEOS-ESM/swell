# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from swell.tasks.base.task_base import taskBase
from swell.utilities.r2d2 import load_r2d2_credentials, get_r2d2_model_name

from datetime import timedelta
import isodate
import os
import r2d2

# --------------------------------------------------------------------------------------------------


class GetBackground(taskBase):

    @staticmethod
    def geos_cf_oper_forecast_start(background_time):
        """Return the GEOS-CF v2 forecast cycle that provides background_time."""
        forecast_start = background_time.replace(hour=9, minute=0, second=0, microsecond=0)

        if background_time < forecast_start:
            forecast_start = forecast_start - timedelta(days=1)

        return forecast_start

    @staticmethod
    def geos_cf_oper_step(background_time, forecast_start_time):
        """Return a GEOS-CF v2 R2D2 step string matching SaveBackground."""
        step_seconds = int((background_time - forecast_start_time).total_seconds())

        if step_seconds % 3600 == 0:
            return f'PT{step_seconds // 3600}H'

        return isodate.duration_isoformat(background_time - forecast_start_time)

    def execute(self) -> None:
        """Acquires background files for a given experiment and cycle

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """

        # Load R2D2 credentials
        # ---------------------
        load_r2d2_credentials(
            self.logger,
            self.platform(),
            r2d2_server=self.config.r2d2_server(default=None),
        )

        r2d2_datastore = self.config.r2d2_datastore(default=None)

        # Get duration into forecast for first background file
        # ----------------------------------------------------
        bkg_steps = []

        # Parse config
        background_frequency = self.config.background_frequency(None)
        horizontal_resolution = self.config.horizontal_resolution()
        window_length = self.config.window_length()
        window_type = self.config.window_type()

        # For experiments with cycle in the suite name:
        # for the first cycle, use background_experiment in config
        # as the experiment id for fetching from r2d2 for cycles after
        # the first, use the current experiment id for fetching from r2d2
        if self.cycle_time_dto() != self.start_cycle_point_dto() and 'cycle' in self.suite_name():
            background_experiment = self.config.r2d2_experiment_id()
        else:
            background_experiment = self.config.background_experiment()

        self.logger.info(f'Fetching background from experiment {background_experiment}')

        # Get window parameters
        local_background_time = self.da_window_params.local_background_time(window_length,
                                                                            window_type)
        analysis_time_iso = self.da_window_params.analysis_time_iso()

        # Add to jedi config rendering dictionary
        self.jedi_rendering.add_key('local_background_time', local_background_time)
        self.jedi_rendering.add_key('marine_models', self.config.marine_models(None))
        self.jedi_rendering.add_key('analysis_time_iso', analysis_time_iso)

        # Convert to datetime durations
        # -----------------------------
        window_length_dur = isodate.parse_duration(window_length)
        forecast_offset_dur = self.da_window_params.analysis_forecast_window_offset(window_length,
                                                                                    dto=True)

        # Duration between the start of the forecast that generated the background
        # and the middle of the current window
        # -------------------------------------------------------------------------------
        forecast_duration_for_background = window_length_dur - forecast_offset_dur

        # If the window type is 4D then remove the window offset as first background
        # occurs at the beginning of the window
        # -------------------------------------------------------------------------------
        if window_type == "4D":
            window_offset_dur = self.da_window_params.window_offset(window_length, dto=True)
            forecast_duration_for_background = forecast_duration_for_background - window_offset_dur

        # Append the list of backgrounds to get with the first background
        # -----------------------------------------------------------------
        bkg_steps.append(isodate.duration_isoformat(forecast_duration_for_background))

        # If background is provided though files get all backgrounds
        # ----------------------------------------------------------
        if window_type == "4D":

            bkg_freq_dur = isodate.parse_duration(background_frequency)

            # Check for a sensible frequency
            # ------------------------------
            if (window_length_dur / bkg_freq_dur) % 2:
                self.logger.abort('Window length not divisible by background frequency')

            # Loop over window
            print('self.cycle_time_dto()', self.cycle_time_dto())
            print('window_offset_dur', window_offset_dur)

            start_date = self.cycle_time_dto() - window_offset_dur
            final_date = self.cycle_time_dto() + window_offset_dur

            loop_date = start_date + bkg_freq_dur

            while loop_date <= final_date:
                duration_in = loop_date - start_date + forecast_duration_for_background
                bkg_steps.append(isodate.duration_isoformat(duration_in))
                loop_date += bkg_freq_dur

        # Get the forecast start time
        # ---------------------------
        forecast_start_time = self.cycle_time_dto() - window_length_dur + forecast_offset_dur

        # Get name of this model component
        # --------------------------------
        model_component = self.get_model()
        use_geos_cf_oper_background = (
            model_component == 'geos_cf'
            and background_experiment == 'geos_cf_oper'
        )

        if use_geos_cf_oper_background:
            self.logger.info(
                'Using GEOS-CF v2 fixed 09Z forecast reference for background fetches.'
            )

        # Loop over background files in the R2D2 config and fetch
        # -------------------------------------------------------
        self.logger.info('Background steps being fetched: ' + ' '.join(str(e) for e in bkg_steps))

        # Get r2d2 dictionary
        r2d2_dict = self.jedi_rendering.render_interface_model('r2d2')

        # Loop over fc
        # ------------
        fc_list = r2d2_dict['fetch']['fc']
        for fc in fc_list:

            # Get file metadata from r2d2 config
            # -----------------------------------
            file_type = fc['file_type']
            target_file_template = fc['filename']
            r2d2_model = fc.get('r2d2_model', get_r2d2_model_name(model_component))

            # Loop over background steps
            # --------------------
            for bkg_step in bkg_steps:

                # Set the datetime format for the output files
                # --------------------------------------------
                background_time = forecast_start_time + isodate.parse_duration(bkg_step)

                # Set the datetime templating in the target file name
                # ---------------------------------------------------
                target_file = background_time.strftime(target_file_template)

                file_extension = file_type.split('.')[-1] if '.' in file_type else 'nc'
                fetch_step = bkg_step
                fetch_date = forecast_start_time.strftime('%Y-%m-%dT%H:%M:%SZ')

                if use_geos_cf_oper_background:
                    geos_cf_forecast_start_time = self.geos_cf_oper_forecast_start(background_time)
                    fetch_step = self.geos_cf_oper_step(background_time, geos_cf_forecast_start_time)
                    fetch_date = geos_cf_forecast_start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
                    file_extension = 'nc4'
                    self.logger.info(
                        f'GEOS-CF v2 background fetch: valid='
                        f'{background_time.strftime("%Y-%m-%dT%H:%M:%SZ")}, '
                        f'date={fetch_date}, step={fetch_step}'
                    )

                fetch_kwargs = dict(
                    item='forecast',
                    target_file=target_file,
                    model=r2d2_model,
                    experiment=background_experiment,
                    file_extension=file_extension,
                    resolution=horizontal_resolution,
                    step=fetch_step,
                    date=fetch_date,
                    file_type=file_type,
                )
                if r2d2_datastore:
                    fetch_kwargs['data_store'] = r2d2_datastore
                r2d2.fetch(**fetch_kwargs)

                # Change permission
                os.chmod(target_file, 0o644)

# --------------------------------------------------------------------------------------------------
