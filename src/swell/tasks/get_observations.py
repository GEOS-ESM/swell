# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from swell.tasks.base.task_base import taskBase
from r2d2 import fetch


# --------------------------------------------------------------------------------------------------


class GetObservations(taskBase):

    def execute(self):

        """Acquires observation files for a given experiment and cycle

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.

           Work Remaining
           --------------
             "tlapse" files need to be fetched.
        """

        # Parse config
        # ------------
        obs_experiment = self.config_get('obs_experiment')
        obs_provider = self.config_get('obs_provider')
        background_time_offset = self.config_get('background_time_offset')
        observations = self.config_get('observations')
        window_length = self.config_get('window_length')
        crtm_coeff_dir = self.config_get('crtm_coeff_dir', None)
        window_offset = self.config_get('window_offset')

        # Get window begin time
        window_begin = self.da_window_params.window_begin(window_offset)
        background_time = self.da_window_params.background_time(window_offset,
                                                                background_time_offset)

        # Add to JEDI template rendering dictionary
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', crtm_coeff_dir)
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Loop over observation operators
        # -------------------------------
        for observation in observations:

            # Open the observation operator dictionary
            # ----------------------------------------
            observation_dict = self.jedi_rendering.render_interface_observations(observation)

            # Fetch observation files
            # -----------------------
            target_file = observation_dict['obs space']['obsdatain']['engine']['obsfile']
            self.logger.info("Processing observation file "+target_file)

            fetch(date=window_begin,
                  target_file=target_file,
                  provider=obs_provider,
                  obs_type=observation,
                  time_window=window_length,
                  type='ob',
                  experiment=obs_experiment)

            # Change permission
            os.chmod(target_file, 0o644)

            # Fetch bias correction files
            # ---------------------------
            if 'obs bias' not in observation_dict:
                continue

            # Satbias
            target_file = observation_dict['obs bias']['input file']
            self.logger.info("Processing satbias file "+target_file)

            fetch(date=background_time,
                  target_file=target_file,
                  provider='gsi',
                  obs_type=observation,
                  type='bc',
                  experiment=obs_experiment,
                  file_type='satbias')

            # Change permission
            os.chmod(target_file, 0o644)

            # Tlapse
            for target_file in self.get_tlapse_files(observation_dict):

                self.logger.info("Processing tlapse file "+target_file)

                fetch(date=background_time,
                      target_file=target_file,
                      provider='gsi',
                      obs_type=observation,
                      type='bc',
                      experiment=obs_experiment,
                      file_type='tlapse')

                # Change permission
                os.chmod(target_file, 0o644)

    # ----------------------------------------------------------------------------------------------

    def get_tlapse_files(self, observation_dict):

        # Function to locate instances of tlapse in the obs operator config

        hash = observation_dict
        if 'obs bias' not in hash:
            return

        hash = hash['obs bias']
        if 'variational bc' not in hash:
            return

        hash = hash['variational bc']
        if 'predictors' not in hash:
            return

        predictors = hash['predictors']
        for p in predictors:
            if 'tlapse' in p:
                yield p['tlapse']

        return
