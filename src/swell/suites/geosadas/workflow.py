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

[scheduler]
    UTC mode = True
    allow implicit tasks = False

{{stall_timeout}}

# --------------------------------------------------------------------------------------------------

[scheduling]

    initial cycle point = 2020-12-15T00:00:00Z
    final cycle point = 2020-12-15T00:00:00Z

    [[graph]]
        R1 = """
            # Clone JEDI source code
            CloneJedi

            # Build JEDI source code by linking
            BuildJediByLinking?
            {% for model_component in model_components %}
            # Stage JEDI static files
            CloneJedi => StageJedi-{{model_component}}
            {% endfor %}

            # Clone geos ana for generating observing system records
            CloneGeosMksi
        """

        T00 = """
            {% for model_component in model_components %}
            # Generate satellite channel records
            CloneGeosMksi[^] => GenerateObservingSystemRecords-{{model_component}}

            # Get and convert bias correction coefficients
            GetGsiBc-{{model_component}} => GsiBcToIoda-{{model_component}}

            # Get and convert ncdiags
            GetGsiNcdiag-{{model_component}} => GsiNcdiagToIoda-{{model_component}}

            # Get background
            GetGeosAdasBackground-{{model_component}}

            # Run Jedi variational executable
            GenerateObservingSystemRecords-{{model_component}} => RenderJediObservations-{{model_component}}
            BuildJediByLinking[^]?  => RunJediVariationalExecutable-{{model_component}}
            StageJedi-{{model_component}}[^] => RunJediVariationalExecutable-{{model_component}}
            GsiBcToIoda-{{model_component}} => RunJediVariationalExecutable-{{model_component}}
            GsiNcdiagToIoda-{{model_component}} => RunJediVariationalExecutable-{{model_component}}
            GetGeosAdasBackground-{{model_component}} => RenderJediObservations-{{model_component}}
            RenderJediObservations-{{model_component}} => RunJediVariationalExecutable-{{model_component}}

            # Clean cycle
            RunJediVariationalExecutable-{{model_component}} => CleanCycle-{{model_component}}
            {% endfor %}
        """

# --------------------------------------------------------------------------------------------------

[runtime]

    # Task defaults
    # -------------

'''  # noqa

# --------------------------------------------------------------------------------------------------


@workflows.register('geosadas')
class Workflow_geosadas(CylcWorkflow):

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
        self.tasks.append(ta.BuildJediByLinking())
        self.tasks.append(ta.CloneGeosMksi())

        for model in self.experiment_dict['model_components']:
            self.tasks.append(ta.GenerateObservingSystemRecords(model=model))
            self.tasks.append(ta.StageJedi(model=model))
            self.tasks.append(ta.GetGsiBc(model=model))
            self.tasks.append(ta.GsiBcToIoda(model=model))
            self.tasks.append(ta.GetGsiNcdiag(model=model))
            self.tasks.append(ta.GsiNcdiagToIoda(model=model))
            self.tasks.append(ta.GetGeosAdasBackground(model=model))
            self.tasks.append(ta.RunJediVariationalExecutable(model=model))
            self.tasks.append(ta.RenderJediObservations(model=model))
            self.tasks.append(ta.CleanCycle(model=model))

# --------------------------------------------------------------------------------------------------
