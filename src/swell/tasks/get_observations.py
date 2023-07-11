# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from swell.tasks.base.task_base import taskBase
from r2d2 import R2D2Data


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
        experiment = self.config_get('obs_experiment')
        provider = self.config_get('obs_provider')
        window_begin = self.config_get('window_begin')
        background_time = self.config_get('background_time')
        observations = self.config_get('observations')
        window_length = self.config_get('window_length')

        os.environ['R2D2_HOST'] = 'localhost'

        # Loop over observation operators
        # -------------------------------
        for observation in observations:

            # Open the observation operator dictionary
            # ----------------------------------------
            observation_dict = self.open_jedi_interface_obs_config_file(observation)
            # Fetch observation files
            # -----------------------
            target_file = observation_dict['obs space']['obsdatain']['engine']['obsfile']

            self.logger.info("Processing observation file "+target_file)

            target_dir = os.path.dirname(target_file)
            os.makedirs(target_dir, exist_ok = True)
            file_extension = os.path.splitext(target_file)[1].replace(".", "")

            R2D2Data.fetch(item             = 'observation'
                          ,target_file      = target_file
                          # ,data_store       = 'swell_store' # Don't specify data_store.  R2D2 will find wherever it exists on local.
                          ,provider         = provider
                          ,observation_type = observation
                          ,file_extension   = file_extension
                          ,window_start     = window_begin
                          ,window_length    = window_length)
                          # ,create_date =
                          # ,mod_date = )

#            fetch(date=window_begin,
#                  target_file=target_file,
#                  provider=provider,
#                  obs_type=observation,
#                  time_window=window_length,
#                  type='ob',
#                  experiment=experiment)

            # Change permission
            os.chmod(target_file, 0o644)

            # Fetch bias correction files
            # ---------------------------
            if 'obs bias' not in observation_dict:
                continue

            # Satbias
            target_file = observation_dict['obs bias']['input file']
            self.logger.info("Processing satbias file "+target_file)

            target_dir = os.path.dirname(target_file)
            os.makedirs(target_dir, exist_ok = True)
            file_extension = os.path.splitext(target_file)[1].replace(".", "")

            R2D2Data.fetch(item             = 'bias_correction'
                          ,target_file      = target_file
                          # ,data_store       = 'swell_store' # Don't specify data_store.  R2D2 will find wherever it exists on local.
                          ,model            = 'geos_atmosphere'
                          ,experiment       = experiment
                          ,provider         = 'gsi'
                          ,observation_type = observation
                          ,file_extension   = file_extension
                          ,file_type        = 'satbias'
                          ,date             = background_time)
                          # ,create_date =
                          # ,mod_date = )

#            fetch(date=background_time,
#                  target_file=target_file,
#                  provider='gsi',
#                  obs_type=observation,
#                  type='bc',
#                  experiment=experiment,
#                  file_type='satbias')

            # Change permission
            os.chmod(target_file, 0o644)

            # Tlapse
            for target_file in list(set(list(self.get_tlapse_files(observation_dict)))):

                self.logger.info("Processing tlapse file "+target_file)

                target_dir = os.path.dirname(target_file)
                os.makedirs(target_dir, exist_ok = True)
                file_extension = os.path.splitext(target_file)[1].replace(".", "")

                R2D2Data.fetch(item             = 'bias_correction'
                              ,target_file      = target_file
                              # ,data_store       = 'swell_store' # Don't specify data_store.  R2D2 will find wherever it exists on local.
                              ,model            = 'geos_atmosphere'
                              ,experiment       = experiment
                              ,provider         = 'gsi'
                              ,observation_type = observation
                              ,file_extension   = file_extension
                              ,file_type        = 'tlapse'
                              ,date             = background_time)
                              # create_date =
                              # ,mod_date = )

#                fetch(date=background_time,
#                      target_file=target_file,
#                      provider='gsi',
#                      obs_type=observation,
#                      type='bc',
#                      experiment=experiment,
#                      file_type='tlapse')

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
