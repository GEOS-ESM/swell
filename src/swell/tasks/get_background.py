# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from swell.tasks.base.task_base import taskBase

from datetime import datetime as dt
import isodate
import os
import re
from r2d2 import fetch


# --------------------------------------------------------------------------------------------------


class GetBackground(taskBase):

    def execute(self):

        """Acquires background files for a given experiment and cycle

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """

        # Current cycle time object
        # -------------------------
        current_cycle = self.config_get('current_cycle')
        current_cycle_dto = dt.strptime(current_cycle, self.get_datetime_format())

        # Get duration into forecast for first background file
        # ----------------------------------------------------
        bkg_steps = []

        # Parse config
        window_type = self.config_get('window_type')
        window_length = self.config_get('window_length')
        window_offset = self.config_get('window_offset')
        background_source = self.config_get('background_source', 'file')
        background_experiment = self.config_get('background_experiment')
        horizontal_resolution = self.config_get('horizontal_resolution')
        forecast_offset = self.config_get('analysis_forecast_window_offset')

        
        # Convert to datetime durations
        window_length_dur = isodate.parse_duration(window_length)
        window_offset_dur = isodate.parse_duration(window_offset)
        forecast_offset_dur = isodate.parse_duration(forecast_offset)

        # Depending on window type get the time of the background
        if window_type == "3D":
            # Single background at the middle of the window
            fcst_length = window_length_dur - forecast_offset_dur
            forecast_start_time = current_cycle_dto - fcst_length
        elif window_type == "4D":
            # Background at the start of the window
            fcst_length = window_length_dur - forecast_offset_dur - window_offset_dur
            forecast_start_time = current_cycle_dto - window_offset_dur - fcst_length

        # Convert to ISO duration string
        fcst_length_iso = isodate.duration_isoformat(fcst_length)
        bkg_steps.append(fcst_length_iso)

        # If background is provided though files get all backgrounds
        # ----------------------------------------------------------
        if window_type == "4D" and background_source == 'file':

            bkg_freq = self.config_get('background_frequency')
            bkg_freq_dur = isodate.parse_duration(bkg_freq)

            # Check for a sensible frequency
            if (window_length_dur/bkg_freq_dur) % 2:
                self.logger.abort('Window length not divisible by background frequency')

            # Loop over window
            start_date = current_cycle_dto - window_offset_dur
            final_date = current_cycle_dto + window_offset_dur

            loop_date = start_date + bkg_freq_dur

            while loop_date <= final_date:
                duration_in = loop_date - start_date + fcst_length
                bkg_steps.append(isodate.duration_isoformat(duration_in))
                loop_date += bkg_freq_dur

        # Loop over background files in the R2D2 config and fetch
        # -------------------------------------------------------
        self.logger.info('Background steps being fetched: '+' '.join(str(e) for e in bkg_steps))

        # Get r2d2 dictionary
        r2d2_dict = self.open_jedi_interface_model_config_file('r2d2')

        # Loop over fc
        for fc in r2d2_dict['fetch']['fc']:

            # Reset target file
            target_file_template = fc['filename']

            # Loop over file types
            for file_type in fc['file_type']:

                # Looop over background steps
                for bkg_step in bkg_steps:

                    # Set the datetime format for the output files
                    background_time = forecast_start_time + isodate.parse_duration(bkg_step)

                    # Set the datetime templating in the target file name
                    target_file = background_time.strftime(target_file_template)

                    # Perform the fetch
                    # fetch(date=forecast_start_time,
                    #       target_file=target_file,
                    #       model='geos',
                    #       file_type='bkg',
                    #       fc_date_rendering='analysis',
                    #       step=bkg_step,
                    #       resolution=horizontal_resolution,
                    #       type='fc',
                    #       experiment=background_experiment)
                    fetch(date=forecast_start_time,
                          target_file=target_file,
                          model='mom6_cice6_UFS',
                          file_type='MOM.res',
                          fc_date_rendering='analysis',
                          step=bkg_step,
                        #   resolution=horizontal_resolution,
                          type='fc',
                          experiment=background_experiment)

                    # Change permission
                    os.chmod(target_file, 0o644)


