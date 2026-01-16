# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import glob
import importlib

from swell.swell_path import get_swell_path
from swell.utilities.case_switching import snake_case_to_camel_case
from swell.tasks.base.task_setup import TaskSetup
from swell.tasks.stage_jedi import Setup as StageJedi

# --------------------------------------------------------------------------------------------------


class root(TaskSetup):
    def set_attributes(self):
        self.script = False
        self.pre_script = "source $CYLC_SUITE_DEF_PATH/modules"
        self.additional_sections = [self.create_new_section('environment',
                                                            {'datetime': '$CYLC_TASK_CYCLE_POINT',
                                                             'config': '$CYLC_SUITE_DEF_PATH/experiment.yaml'})]  # noqa


class StageJediCycle(StageJedi):
    def set_attributes(self):
        super().set_attributes()
        self.base_name = "StageJedi"
        self.scheduling_name = "StageJediCycle-{model}"
        self.is_cycling = True
        self.is_model = True


class sync_point(TaskSetup):
    def set_attributes(self):
        self.script = "true"


# --------------------------------------------------------------------------------------------------

class TaskAttributes():
    def __init__(self) -> None:
        task_path = os.path.join(get_swell_path(), 'tasks', '*.py')

        setattr(self, 'root', root)
        setattr(self, 'StageJediCycle', StageJediCycle)
        setattr(self, 'sync_point', sync_point)

        for task_file in glob.glob(task_path):
            module_name = os.path.basename(task_file).split('.py')[0]
            module_path = f'swell.tasks.{module_name}'

            try:
                module = importlib.import_module(module_path)
                setup = getattr(module, 'Setup')

                task_name = snake_case_to_camel_case(module_name)

                setattr(self, task_name, setup)

            except AttributeError:
                pass

    def get(self, task_name):
        return getattr(self, task_name)


# --------------------------------------------------------------------------------------------------

task_attributes = TaskAttributes()

# --------------------------------------------------------------------------------------------------
