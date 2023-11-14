# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from swell.tasks.base.task_base import taskBase

import isodate
import os
#from r2d2 import fetch


# --------------------------------------------------------------------------------------------------

r2d2_model_dict = {
    'geos_atmosphere': 'geos',
    'geos_ocean': 'mom6_cice6_UFS',
}


# --------------------------------------------------------------------------------------------------

class GetBackground3d(taskBase):

    def execute(self):

        """Acquires 3D background files for a given experiment and cycle

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """

        bkg_step = None

        # Parse config
        background_experiment = self.config.background_experiment()
        forecast_offset = self.config.analysis_forecast_window_offset()
        horizontal_resolution = self.config.horizontal_resolution()
        window_length = self.config.window_length()
        window_offset = self.config.window_offset()

        # Get window parameters
        local_background_time = self.da_window_params.local_background_time(window_offset, '3D')

        # Add to jedi config rendering dictionary
        self.jedi_rendering.add_key('local_background_time', local_background_time)

        # Convert to datetime durations
        # -----------------------------
        window_length_dur = isodate.parse_duration(window_length)
        forecast_offset_dur = isodate.parse_duration(forecast_offset)

        # Duration between the start of the forecast that generated the background
        # and the middle of the current window
        # -------------------------------------------------------------------------------
        forecast_duration_for_background = window_length_dur - forecast_offset_dur

        # Append the list of backgrounds to get with the first background
        # -----------------------------------------------------------------
        bkg_step = isodate.duration_isoformat(forecast_duration_for_background)

        # Get the forecast start time
        # ---------------------------
        forecast_start_time = self.cycle_time_dto() - window_length_dur + forecast_offset_dur

        # Get name of this model component
        # --------------------------------
        model_component = self.get_model()

        # Loop over background files in the R2D2 config and fetch
        # -------------------------------------------------------
        self.logger.info(f"Background step being fetched: {bkg_step}")

        # Get r2d2 dictionary
        r2d2_dict = self.jedi_rendering.render_interface_model('r2d2')

        # Loop over fc
        # ------------
        for fc in r2d2_dict['fetch']['fc']:

            # Reset target file
            # --------------------
            file_type = fc['file_type']
            target_file_template = fc['filename']

            # Set the datetime format for the output files
            # --------------------------------------------
            background_time = forecast_start_time + isodate.parse_duration(bkg_step)

            # Set the datetime templating in the target file name
            # ---------------------------------------------------
            target_file = background_time.strftime(target_file_template)

            args = {'data': str(forecast_start_time),          
                    'target_file': str(target_file),                           
                    'model': str(r2d2_model_dict[model_component]),            
                    'file_type': str(file_type),                               
                    'fc_date_rendering': 'analysis',                           
                    'step': str(bkg_step),                                     
                    'resolution': str(horizontal_resolution),                  
                    'type': 'fc',                                              
                    'experiment': str(background_experiment)}

            print(str(args), '\n')

            # fetch(
            #     date=forecast_start_time,
            #     target_file=target_file,
            #     model=r2d2_model_dict[model_component],
            #     file_type=file_type,
            #     fc_date_rendering='analysis',
            #     step=bkg_step,
            #     resolution=horizontal_resolution,
            #     type='fc',
            #     experiment=background_experiment)

            # # Change permission
            # os.chmod(target_file, 0o644)

# --------------------------------------------------------------------------------------------------
