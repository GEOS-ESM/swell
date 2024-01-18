# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.tasks.base.task_base import taskBase
from swell.utilities.run_jedi_executables import jedi_dictionary_iterator, run_executable


# --------------------------------------------------------------------------------------------------


class RunJediHofxEnsembleExecutable(taskBase):

    # ----------------------------------------------------------------------------------------------

    def execute(self):

        # Jedi application name
        # ---------------------
        # jedi_application = 'ensemblehofx'

        # Ensemble hofx components
        ensemble_hofx_packets = self.config.ensemble_hofx_packets()
        ensemble_hofx_strategy = self.config.ensemble_hofx_strategy()
        ensemble_num_members = self.config.ensemble_num_members()

        if ensemble_num_numbers%ensemble_hofx_packets != 0:
            raise ValueError("Number of ensemble packets must evenly divide number of ensemble members!")

        self.jedi_rendering.add_key('ensemble_hofx_packets', ensemble_hofx_packets)
        self.jedi_rendering.add_key('ensemble_hofx_strategy', ensemble_hofx_strategy)
        self.jedi_rendering.add_key('ensemble_num_members', ensemble_num_members)

        self.logger.info('Running ensemble hofx strategy %s in %i packets'%(ensemble_hofx_strategy, ensemble_packets))

# --------------------------------------------------------------------------------------------------
