# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
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
        experiment = self.config_get('obs_experiment')
        window_begin = self.config_get('window_begin')
        background_time = self.config_get('background_time')
        observations = self.config_get('observations')

        # Loop over observation operators
        # -------------------------------
        for observation in observations:

            # Open the observation operator dictionary
            # ----------------------------------------
            observation_dict = self.open_jedi_interface_obs_config_file(observation)

            print(observation_dict)

            exit()

            # Fetch observation files
            # -----------------------
            name = ob['obs space']['name']
            target_file = ob['obs space']['obsdatain']['engine']['obsfile']
            self.logger.info("Processing observation file "+target_file)

            fetch(date=window_begin,
                  target_file=target_file,
                  provider='ncdiag',
                  obs_type=name,
                  type='ob',
                  experiment=experiment)

            # Change permission
            os.chmod(target_file, 0o644)

            # Fetch bias correction files
            # ---------------------------
            if 'obs bias' not in ob:
                continue

            # Satbias
            target_file = ob['obs bias']['input file']
            self.logger.info("Processing satbias file "+target_file)

            fetch(date=background_time,
                  target_file=target_file,
                  provider='gsi',
                  obs_type=name,
                  type='bc',
                  experiment=experiment,
                  file_type='satbias')

            # Change permission
            os.chmod(target_file, 0o644)

            # Tlapse
            for target_file in self.get_tlapse_files(ob):

                self.logger.info("Processing tlapse file "+target_file)

                fetch(date=background_time,
                      target_file=target_file,
                      provider='gsi',
                      obs_type=name,
                      type='bc',
                      experiment=experiment,
                      file_type='tlapse')

                # Change permission
                os.chmod(target_file, 0o644)

    # ----------------------------------------------------------------------------------------------

    def get_tlapse_files(self, ob):

        # Function to locate instanses of tlapse in the obs operator config

        hash = ob
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
