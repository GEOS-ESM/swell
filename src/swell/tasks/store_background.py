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
from r2d2 import R2D2Data


# --------------------------------------------------------------------------------------------------


class StoreBackground(taskBase):

    def execute(self):

        """Store background files for a given experiment and cycle in R2D2

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """

        # Shortcuts to base objects
        # -------------------------
        cfg = self.config
        logger = self.logger

        # Current cycle time object
        # -------------------------
        current_cycle = cfg.get('current_cycle')
        current_cycle_dto = dt.strptime(current_cycle, cfg.dt_format)

        # Get duration into forecast for first background file
        # ----------------------------------------------------
        bkg_steps = []

        # Parse config
        window_type = cfg.get('window_type')
        window_length = cfg.get('window_length')
        window_offset = cfg.get('window_offset')

        # Position relative to center of the window where forecast starts
        forecast_offset = cfg.get('analysis_forecast_window_offset')

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
        bkg_info = cfg.get('backgrounds')

        if window_type == "4D" and bkg_info['background source'] == 'file':

            bkg_freq = bkg_info['background frequency']
            bkg_freq_dur = isodate.parse_duration(bkg_freq)

            # Check for a sensible frequency
            if (window_length_dur/bkg_freq_dur) % 2:
                logger.abort('Window length not divisible by background frequency')

            # Loop over window
            start_date = current_cycle_dto - window_offset_dur
            final_date = current_cycle_dto + window_offset_dur

            loop_date = start_date + bkg_freq_dur

            while loop_date <= final_date:
                duration_in = loop_date - start_date + fcst_length
                bkg_steps.append(isodate.duration_isoformat(duration_in))
                loop_date += bkg_freq_dur

        # Loop over background files in the R2D2 config and store
        # -------------------------------------------------------
        logger.info('Background steps being fetched: '+' '.join(str(e) for e in bkg_steps))

        # Background dictionary from config
        background_dict = cfg.get('BACKGROUND')

        # Get r2d2 dictionary
        r2d2_dict = cfg.get('R2D2')

        os.environ['R2D2_HOST'] = 'localhost'

        # Loop over fc
        for fc in r2d2_dict['store']['fc']:

            # Reset source file
            source_file_template = os.path.split(background_dict['filename'])[1]

            # Datetime format to use
            user_date_format = fc['user_date_format']

            # Loop over file types
            for file_type in fc['file_type']:

                # Replace filetype in source_file_template
                source_file_type_template = source_file_template.replace("$(file_type)", file_type)

                # Looop over background steps
                for bkg_step in bkg_steps:

                    # Set the datetime format for the output files
                    background_time = forecast_start_time + isodate.parse_duration(bkg_step)
                    valid_time_str = background_time.strftime(user_date_format)

                    # Set the source file name
                    source_file = source_file_type_template.replace("$(valid_date)", valid_time_str)
                    source_file = os.path.join(cfg.get('cycle_dir'), source_file)

                    file_extension = os.path.splitext(source_file)[1].replace(".", "")

                    # Perform the store
                    R2D2Data.store(item           = 'forecast'
                                  ,source_file    = source_file
                                  ,data_store     = 'swell-r2d2'
                                  ,model          = 'geos'
                                  ,experiment     = bkg_info['background experiment']
                                  ,file_extension = file_extension
                                  ,resolution     = cfg.get('horizontal_resolution')
                                  #,domain = 
                                  ,file_type      = 'bkg'
                                  ,step           = bkg_step
                                  #,tile = 
                                  #,member = 
                                  ,date           = forecast_start_time)
                                  # ,create_date = 
                                  # ,mod_date = )


#                    store(date=forecast_start_time,
#                          source_file=target_file,
#                          model='geos',
#                          file_type='bkg',
#                          fc_date_rendering='analysis',
#                          step=bkg_step,
#                          resolution=cfg.get('horizontal_resolution'),
#                          type='fc',
#                          experiment=bkg_info['background experiment'])

