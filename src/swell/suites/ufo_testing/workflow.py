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
from swell.suites.base.suite_attributes import workflows

# --------------------------------------------------------------------------------------------------

template_str = '''
# --------------------------------------------------------------------------------------------------

# Cylc suite for executing geos_atmosphere ObsFilters tests

# --------------------------------------------------------------------------------------------------

[scheduler]
    UTC mode = True
    allow implicit tasks = False

{{stall_timeout}}

# --------------------------------------------------------------------------------------------------

[scheduling]

    initial cycle point = {{start_cycle_point}}
    final cycle point = {{final_cycle_point}}
    runahead limit = {{runahead_limit}}

    [[graph]]
        R1 = """
            # Triggers for non cycle time dependent tasks
            # -------------------------------------------
            # Clone JEDI source code
            CloneJedi

            # Build JEDI source code by linking
            CloneJedi => BuildJediByLinking?

            # If not able to link to build create the build
            BuildJediByLinking:fail? => BuildJedi

            # Clone geos ana for generating observing system records
            CloneGeosMksi
        """

        {% for cycle_time in cycle_times %}
        {{cycle_time.cycle_time}} = """

            # Generate satellite channel records
            CloneGeosMksi[^] => GenerateObservingSystemRecords

            # Convert bias correction to ioda
            GetGsiBc
            GetGsiBc => GsiBcToIoda
            BuildJediByLinking[^]? | BuildJedi[^]  => GsiBcToIoda

            # Convert ncdiags to ioda
            GetGsiNcdiag
            GetGsiNcdiag => GsiNcdiagToIoda
            BuildJediByLinking[^]? | BuildJedi[^]  => GsiNcdiagToIoda

            GetGeovals

            GsiNcdiagToIoda => RenderJediObservations

            # Run Jedi hofx executable
            RenderJediObservations => RunJediUfoTestsExecutable
            GenerateObservingSystemRecords => RunJediUfoTestsExecutable
            GsiNcdiagToIoda => RunJediUfoTestsExecutable
            GsiBcToIoda => RunJediUfoTestsExecutable
            GetGeovals => RunJediUfoTestsExecutable

            # EvaObservations
            RunJediUfoTestsExecutable => EvaObservations

            # Clean up large files
            EvaObservations => CleanCycle

        """
        {% endfor %}

# --------------------------------------------------------------------------------------------------

[runtime]

    # Task defaults
    # -------------
'''

# --------------------------------------------------------------------------------------------------


@workflows.register('ufo_testing')
class Workflow_ufo_testing(CylcWorkflow):

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
        self.tasks.append(ta.CloneJedi())
        self.tasks.append(ta.BuildJedi())
        self.tasks.append(ta.BuildJediByLinking())

        for model in self.experiment_dict['model_components']:
            self.tasks.append(ta.CloneGeosMksi(model=model))
            self.tasks.append(ta.GenerateObservingSystemRecords(model=model))
            self.tasks.append(ta.GetGsiBc(model=model))
            self.tasks.append(ta.GsiBcToIoda(model=model))
            self.tasks.append(ta.GetGsiNcdiag(model=model))
            self.tasks.append(ta.GsiNcdiagToIoda(model=model))
            self.tasks.append(ta.RenderJediObservations(model=model))
            self.tasks.append(ta.RunJediUfoTestsExecutable(model=model))
            self.tasks.append(ta.GetGeovals(model=model))
            self.tasks.append(ta.EvaObservations(model=model))
            self.tasks.append(ta.CleanCycle(model=model))

# --------------------------------------------------------------------------------------------------
