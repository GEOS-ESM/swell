# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from swell.tasks.base.task_base import taskBase
from swell.utilities.r2d2 import create_r2d2_config

import isodate
import os
from r2d2 import fetch


# --------------------------------------------------------------------------------------------------

r2d2_model_dict = {
    'geos_atmosphere': 'geos',
    'geos_marine': 'mom6_cice6_UFS',
}


# --------------------------------------------------------------------------------------------------

class GetBackground(taskBase):

    def execute(self):

        """Acquires background files for a given experiment and cycle

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """

        # Get duration into forecast for first background file
        # ----------------------------------------------------
        bkg_steps = []

        # Parse config
        background_experiment = self.config.background_experiment()
        background_frequency = self.config.background_frequency(None)
        forecast_offset = self.config.analysis_forecast_window_offset()
        horizontal_resolution = self.config.horizontal_resolution()
        window_length = self.config.window_length()
        window_offset = self.config.window_offset()
        window_type = self.config.window_type()
        r2d2_local_path = self.config.r2d2_local_path()

        # Get window parameters
        local_background_time = self.da_window_params.local_background_time(window_offset,
                                                                            window_type)

        # Add to jedi config rendering dictionary
        self.jedi_rendering.add_key('local_background_time', local_background_time)

        # Set R2D2 config file
        # --------------------
        create_r2d2_config(self.logger, self.platform(), self.cycle_dir(), r2d2_local_path)

        # Convert to datetime durations
        # -----------------------------
        window_length_dur = isodate.parse_duration(window_length)
        forecast_offset_dur = isodate.parse_duration(forecast_offset)

        # Duration between the start of the forecast that generated the background
        # and the middle of the current window
        # -------------------------------------------------------------------------------
        forecast_duration_for_background = window_length_dur - forecast_offset_dur

        # If the window type is 4D then remove the window offset as first background
        # occurs at the beginning of the window
        # -------------------------------------------------------------------------------
        if window_type == "4D":
            window_offset_dur = isodate.parse_duration(window_offset)
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
            if (window_length_dur/bkg_freq_dur) % 2:
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

        # Loop over background files in the R2D2 config and fetch
        # -------------------------------------------------------
        self.logger.info('Background steps being fetched: '+' '.join(str(e) for e in bkg_steps))

        # Get r2d2 dictionary
        r2d2_dict = self.jedi_rendering.render_interface_model('r2d2')

        # Loop over fc
        # ------------
        for fc in r2d2_dict['fetch']['fc']:

            # Reset target file
            # --------------------
            file_type = fc['file_type']
            target_file_template = fc['filename']

            # Loop over background steps
            # --------------------
            for bkg_step in bkg_steps:

                # Set the datetime format for the output files
                # --------------------------------------------
                background_time = forecast_start_time + isodate.parse_duration(bkg_step)

                # Set the datetime templating in the target file name
                # ---------------------------------------------------
                target_file = background_time.strftime(target_file_template)

                fetch(
                    date=forecast_start_time,
                    target_file=target_file,
                    model=r2d2_model_dict[model_component],
                    file_type=file_type,
                    fc_date_rendering='analysis',
                    step=bkg_step,
                    resolution=horizontal_resolution,
                    type='fc',
                    experiment=background_experiment)

                # Change permission
                os.chmod(target_file, 0o644)

# --------------------------------------------------------------------------------------------------
