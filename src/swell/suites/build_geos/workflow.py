# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.cylc_workflow import CylcWorkflow
from swell.tasks.base.task_attributes import TaskAttributes as ta

# --------------------------------------------------------------------------------------------------

template_str = '''
# --------------------------------------------------------------------------------------------------

# Cylc suite for building the GEOS model

# --------------------------------------------------------------------------------------------------

[scheduler]
    allow implicit tasks = False

# --------------------------------------------------------------------------------------------------

[scheduling]

    [[graph]]
        R1 = """
           CloneGeos => BuildGeosByLinking?

           BuildGeosByLinking:fail? => BuildGeos
        """

# --------------------------------------------------------------------------------------------------

[runtime]

    # Task defaults
    # -------------

'''

# --------------------------------------------------------------------------------------------------


class Workflow_build_geos(CylcWorkflow):

    def get_workflow_string(self):
        workflow_str = self.default_header()
        workflow_str += template_string_jinja2(logger=self.logger,
                                               templated_string=template_str,
                                               dictionary_of_templates=self.experiment_dict,
                                               allow_unresolved=True)

        for task in self.tasks:
            workflow_str += task.runtime_string(self.experiment_dict,
                                                self.slurm_external)

        return workflow_str

    def set_tasks(self) -> list:

        self.tasks.append(ta.root())
        self.tasks.append(ta.CloneGeos())
        self.tasks.append(ta.BuildGeos())
        self.tasks.append(ta.BuildGeosByLinking())

# --------------------------------------------------------------------------------------------------
