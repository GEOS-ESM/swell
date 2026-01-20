# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import glob
import importlib
import pkgutil

from swell.swell_path import get_swell_path
from swell.utilities.case_switching import snake_case_to_camel_case
from swell.tasks.base.task_setup import TaskSetup

# --------------------------------------------------------------------------------------------------


class root(TaskSetup):
    def set_attributes(self):
        self.script = False
        self.pre_script = "source $CYLC_SUITE_DEF_PATH/modules"
        self.additional_sections = [self.create_new_section('environment',
                                                            {'datetime': '$CYLC_TASK_CYCLE_POINT',
                                                             'config': '$CYLC_SUITE_DEF_PATH/experiment.yaml'})]  # noqa


class sync_point(TaskSetup):
    def set_attributes(self):
        self.script = "true"


# --------------------------------------------------------------------------------------------------

def discover_plugins(package):

    for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_module_name = f"{package.__name__}.{module_name}"

        importlib.import_module(full_module_name)

# --------------------------------------------------------------------------------------------------

class TaskAttributes():
    def __init__(self) -> None:
        setattr(self, 'root', root)
        setattr(self, 'StageJediCycle', StageJediCycle)
        setattr(self, 'sync_point', sync_point)

    def register(self, name):
        def wrapper(cls):
            setattr(self, name, cls)
            return cls
        return wrapper

    def get(self, task_name):
        return getattr(self, task_name)


# --------------------------------------------------------------------------------------------------

task_attributes = TaskAttributes()

import swell.tasks
discover_plugins(swell.tasks)

# --------------------------------------------------------------------------------------------------
