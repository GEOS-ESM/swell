# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import swell.tasks
from swell.tasks.base.task_setup import TaskSetup
from swell.utilities.plugins import discover_plugins

# --------------------------------------------------------------------------------------------------

'''
The TaskAttributes class provides tracking of TaskSetup classes, which should be defined in each
task's file. It handles this by providing a wrapper method to register each class.

Attributes:
root and sync_point: Setup for tasks used swell-wide that don't require separate files
discover_plugins: Handles discovery of packages, which then run the register hooks when imported
TaskAttributes: class that registers TaskSetup classes in each task file

Example for task registry:
<src/swell/tasks/example.py>

from swell.tasks.base.task_attributes import task_attributes

@task_attributes.register('Example')
class Setup(TaskSetup):
    def __init__(self):
        pass
'''

# --------------------------------------------------------------------------------------------------


class root(TaskSetup):
    def set_attributes(self):
        # root is a precursor to all tasks, it runs the pre-script before any task's script
        self.script = False
        self.pre_script = "source $CYLC_SUITE_DEF_PATH/modules"
        self.additional_sections = [self.create_new_section('environment',
                                                            {'datetime': '$CYLC_TASK_CYCLE_POINT',
                                                             'config': '$CYLC_SUITE_DEF_PATH/experiment.yaml'})]  # noqa


class sync_point(TaskSetup):
    # placeholder task to check run dependencies in cylc graph
    # The command "true" is run in the shell as a placeholder
    def set_attributes(self):
        self.script = "true"


# --------------------------------------------------------------------------------------------------


class TaskAttributes():
    def __init__(self) -> None:
        setattr(self, 'root', root)
        setattr(self, 'sync_point', sync_point)

    def register(self, name):
        '''Provides wrapper to register class using <name>.

        Parameters:
        name: Name to refer to Setup object
        '''
        def wrapper(cls):
            setattr(self, name, cls)
            return cls
        return wrapper

    def get(self, task_name):
        return getattr(self, task_name)


# --------------------------------------------------------------------------------------------------

task_attributes = TaskAttributes()

discover_plugins(swell.tasks)

# --------------------------------------------------------------------------------------------------
