# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.tasks.base.task_base import taskBase
from swell.tasks.base.task_setup import TaskSetup
from swell.tasks.base.task_attributes import task_attributes
# import swell.configuration.question_defaults as qd

# --------------------------------------------------------------------------------------------------

task_name = 'SaveRestart'


@task_attributes.register(task_name)
class Setup(TaskSetup):
    def set_defaults(self):
        self.base_name = task_name
        self.is_cycling = True
        self.model_dep = True

# --------------------------------------------------------------------------------------------------


class SaveRestart(taskBase):

    def execute(self):

        """
        Placeholder for non-GEOS-CF restart storage.

        GEOS-CF restart storage is implemented in SaveRestartCf. Marine/coupled workflows still
        define SaveRestart tasks in their Cylc graphs, but their restart storage path is pending a
        separate implementation.
        """

        self.logger.info('SaveRestart is not implemented for this workflow; skipping.')

# --------------------------------------------------------------------------------------------------
