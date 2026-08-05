#!jinja2
# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.jinja2 import template_string_jinja2
from swell.suites.base.cylc_workflow import CylcWorkflow
from swell.tasks.base.task_attributes import task_attributes as ta
from swell.tasks.base.task_setup import TaskSetup
from swell.suites.base.suite_attributes import workflows

# --------------------------------------------------------------------------------------------------

template_str = '''
# --------------------------------------------------------------------------------------------------

# Cylc suite for Geos forecast without DA

# --------------------------------------------------------------------------------------------------

[scheduler]
    UTC mode = True
    allow implicit tasks = False

{{stall_timeout}}

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
            GetCoupledGeosRestart => PrepCoupledGeosRunDir

            # Get first set of restarts
            BuildGeosByLinking? | BuildGeos  => RunGeos
        """

        {% for cycle_time in cycle_times %}
        {{cycle_time}} = """

            # Run Geos Executable
            PrepCoupledGeosRunDir => RunGeos
            MoveForecastRestart[-PT6H] => PrepCoupledGeosRunDir

            # Move restart to next cycle
            RunGeos => MoveForecastRestart

        """
        {% endfor %}

# --------------------------------------------------------------------------------------------------

[runtime]

    # Task defaults
    # -------------

'''


class RunGeos(TaskSetup):
    def set_defaults(self):
        self.base_name = 'RunGeos'
        self.is_cycling = True
        self.script = '{{experiment_root}}/{{experiment_id}}/GEOSgcm/forecast/gcm_run.j'
        self.slurm = {}

# --------------------------------------------------------------------------------------------------


@workflows.register('forecast_coupled_geos')
class Workflow_forecast_coupled_geos(CylcWorkflow):

    def get_workflow_string(self):
        workflow_str = self.default_header()

        self.experiment_dict['stall_timeout'] = """\
        {% if environ.get('SWELL_CYLC_TIMEOUT') %}
        [[events]]
        stall timeout = {{environ['SWELL_CYLC_TIMEOUT']}}
        {% endif %}"""

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
        self.tasks.append(ta.PrepCoupledGeosRunDir())
        self.tasks.append(ta.GetCoupledGeosRestart())
        self.tasks.append(ta.MoveForecastRestart())
        self.tasks.append(RunGeos())

# --------------------------------------------------------------------------------------------------
