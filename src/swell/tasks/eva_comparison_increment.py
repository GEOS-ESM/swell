# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import yaml

from eva.eva_driver import eva

from swell.tasks.base.task_base import taskBase
from swell.utilities.jinja2 import template_string_jinja2

# --------------------------------------------------------------------------------------------------


class EvaComparisonIncrement(taskBase):

    def execute(self) -> None:

        experiment_paths = self.config.comparison_experiment_paths()

        experiment_path_1 = experiment_paths[0]

        experiment_file_path_1 = os.path.join(os.path.basename(experiment_path_1), 'experiment.yaml')

        task_1 = taskBase(config_input=experiment_file_path_1,
                          datetime_input=self.cycle_time(),
                          model=self.get_model(),
                          ensemblePacket=self.get_ensemble_packet(),
                          task_name='taskBase',
                          test_iteration=None,
                          test_output=None)
        
        print(task_1.cycle_dir())