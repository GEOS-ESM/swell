# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.jinja2 import template_string_jinja2
from swell.suites.base.cylc_workflow import CylcWorkflow
from swell.tasks.base.task_attributes import task_attributes as ta
from swell.suites.base.suite_attributes import workflows

# --------------------------------------------------------------------------------------------------

template_str = '''
# --------------------------------------------------------------------------------------------------

# Cylc suite for Geos forecast without DA

# --------------------------------------------------------------------------------------------------

[scheduler]
    UTC mode = True
    allow implicit tasks = False

# --------------------------------------------------------------------------------------------------

[scheduling]

    initial cycle point = {{start_cycle_point}}
    final cycle point = {{final_cycle_point}}

    [[graph]]
        R1 = """
            # Triggers for non cycle time dependent tasks
            # -------------------------------------------
            # Clone Geos source code
            CloneGeos

            # Build Geos source code by linking
            CloneGeos => BuildGeosByLinking?

            # If not able to link to build create the build
            BuildGeosByLinking:fail? => BuildGeos

            # Need first set of restarts to run model
            GetGeosRestart => PrepGeosRunDir

            # Get first set of restarts
            BuildGeosByLinking? | BuildGeos  => RunGeosExecutable
        """

        {% for cycle_time in cycle_times %}
        {{cycle_time}} = """

            # Run Geos Executable
            PrepGeosRunDir => RunGeosExecutable
            MoveForecastRestart[-PT6H] => PrepGeosRunDir

            # Move restart to next cycle
            RunGeosExecutable => MoveForecastRestart

            # Save restarts if requested
            # MoveForecastRestart[-PT6H] => SaveRestart

            # Remove Run Directory
            MoveForecastRestart => RemoveForecastDir
        """
        {% endfor %}

# --------------------------------------------------------------------------------------------------

[runtime]

    # Task defaults
    # -------------

'''

# --------------------------------------------------------------------------------------------------


@workflows.register('forecast_geos')
class Workflow_forecast_geos(CylcWorkflow):

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
        self.tasks.append(ta.BuildGeosByLinking())
        self.tasks.append(ta.BuildGeos())
        self.tasks.append(ta.GetGeosRestart())
        self.tasks.append(ta.PrepGeosRunDir())
        self.tasks.append(ta.RunGeosExecutable())
        self.tasks.append(ta.MoveForecastRestart())
        self.tasks.append(ta.SaveRestart())
        self.tasks.append(ta.RemoveForecastDir())

# --------------------------------------------------------------------------------------------------
