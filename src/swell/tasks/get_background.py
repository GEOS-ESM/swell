# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import importlib

import isodate
from swell.tasks.base.task_base import taskBase
#from r2d2 import fetch


# --------------------------------------------------------------------------------------------------

r2d2_model_dict = {
    'geos_atmosphere': 'geos',
    'geos_ocean': 'mom6_cice6_UFS',
}


# --------------------------------------------------------------------------------------------------

class GetBackground(taskBase):

    def _fetch_all(self, background_prep, r2d2_dict, model_component):

        # Loop over fc
        # ------------
        for fc in r2d2_dict['fetch']['fc']:

            # Reset target file
            # --------------------
            file_type = fc['file_type']
            target_file_template = fc['filename']

            # Loop over background steps
            # --------------------
            for bkg_step in background_prep.bkg_steps:

                # Set the datetime format for the output files
                # --------------------------------------------
                background_time = background_prep.forecast_start_time +\
                                  isodate.parse_duration(bkg_step)

                # Set the datetime templating in the target file name
                # ---------------------------------------------------
                target_file = background_time.strftime(target_file_template)

                args = {'data': str(background_prep.forecast_start_time),
                        'target_file': str(target_file),
                        'model': str(r2d2_model_dict[model_component]),
                        'file_type': str(file_type),
                        'fc_date_rendering': 'analysis',
                        'step': str(bkg_step),
                        'resolution': str(background_prep.horizontal_resolution),
                        'type': 'fc',
                        'experiment': str(background_prep.background_experiment)}

                print(str(args), '\n')

                # fetch(
                #     date=background_prep.forecast_start_time,
                #     target_file=target_file,
                #     model=r2d2_model_dict[model_component],
                #     file_type=file_type,
                #     fc_date_rendering='analysis',
                #     step=bkg_step,
                #     resolution=horizontal_resolution,
                #     type='fc',
                #     experiment=background_experiment)
                #
                # # Change permission
                # os.chmod(target_file, 0o644)

    def execute(self):

        """Acquires background files for a given experiment and cycle

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """

        window_type = self.config.window_type()

        # Delegate a "prep background" object.
        prep_background_module = importlib.import_module(".prep_background", package=__package__)
        prep_background_class = getattr(prep_background_module, f"PrepBackground{window_type}") # {window_type}")

        # Initialize background_prep object
        background_prep = prep_background_class.fromConfig(self.config)

        # Get window parameters
        local_background_time =\
            self.da_window_params.local_background_time(background_prep.window_offset,
                                                        window_type)

        # Add to jedi config rendering dictionary
        self.jedi_rendering.add_key('local_background_time', local_background_time)

        # Prepare all background parameters
        background_prep.prep(cycle_time_dto = self.cycle_time_dto())

        # Get name of this model component
        model_component = self.get_model()

        self.logger.info('Background steps being fetched: ' +\
                         ' '.join(str(e) for e in background_prep.bkg_steps))

        # Get r2d2 dictionary
        r2d2_dict = self.jedi_rendering.render_interface_model('r2d2')

        # Loop over background files in the R2D2 config and fetch
        self._fetch_all(background_prep, r2d2_dict, model_component)

