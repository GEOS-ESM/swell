# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.jinja2 import template_string_jinja2
from swell.suites.base.cylc_workflow import CylcWorkflow
from swell.tasks.base.task_attributes import task_attributes as ta
from swell.suites.base.all_suites import workflows

# --------------------------------------------------------------------------------------------------

template_str = '''
# --------------------------------------------------------------------------------------------------

# Cylc suite for executing JEDI-based h(x)

# --------------------------------------------------------------------------------------------------

[scheduler]
    UTC mode = True
    allow implicit tasks = False

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

            {% for model_component in model_components %}
            # Clone geos ana for generating observing system records
            CloneGeosMksi-{{model_component}}
            {% endfor %}
        """

        {% for cycle_time in cycle_times %}
        {{cycle_time.cycle_time}} = """
        {% for model_component in model_components %}
        {% if cycle_time[model_component] %}

            # Task triggers for: {{model_component}}
            # ------------------
            # Generate satellite channel records
            CloneGeosMksi-{{model_component}}[^] => GenerateObservingSystemRecords-{{model_component}}

            # Get background, provide a way to get background directly from GEOS experiment
            GetBackgroundGeosExperiment-{{model_component}} :fail? => GetBackground-{{model_component}}

            # Get observations
            GetObsNotInR2d2-{{model_component}}: fail? => GetObservations-{{model_component}}

            # Perform staging that is cycle dependent
            StageJediCycle-{{model_component}}

            # Run Jedi hofx executable
            BuildJediByLinking[^]? | BuildJedi[^]  => RunJediHofxExecutable-{{model_component}}
            CloneJedi[^] => StageJediCycle-{{model_component}}
            StageJediCycle-{{model_component}} => RunJediHofxExecutable-{{model_component}}
            GetBackgroundGeosExperiment-{{model_component}}? | GetBackground-{{model_component}} => RunJediHofxExecutable-{{model_component}}
            GetObsNotInR2d2-{{model_component}}? | GetObservations-{{model_component}} => RenderJediObservations-{{model_component}}
            RenderJediObservations-{{model_component}} => RunJediHofxExecutable-{{model_component}}
            GenerateObservingSystemRecords-{{model_component}} => RunJediHofxExecutable-{{model_component}}

            # EvaObservations
            RunJediHofxExecutable-{{model_component}} => EvaObservations-{{model_component}}

            # Save observations
            RunJediHofxExecutable-{{model_component}} => SaveObsDiags-{{model_component}}

            # Clean up large files
            EvaObservations-{{model_component}} & SaveObsDiags-{{model_component}} =>
            CleanCycle-{{model_component}}

        {% endif %}
        {% endfor %}
        """
        {% endfor %}

# --------------------------------------------------------------------------------------------------

[runtime]

    # Task defaults
    # -------------

'''  # noqa

# --------------------------------------------------------------------------------------------------


@workflows.register('hofx')
class Workflow_hofx(CylcWorkflow):

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
        self.tasks.append(ta.CloneJedi())
        self.tasks.append(ta.BuildJedi())
        self.tasks.append(ta.BuildJediByLinking())
        self.tasks.append(ta.CloneGeosMksi())

        for model in self.experiment_dict['model_components']:
            self.tasks.append(ta.CloneGeosMksi(model=model))
            self.tasks.append(ta.GenerateObservingSystemRecords(model=model))
            self.tasks.append(ta.GetBackgroundGeosExperiment(model=model))
            self.tasks.append(ta.GetBackground(model=model))
            self.tasks.append(ta.GetObservations(model=model))
            self.tasks.append(ta.GetObsNotInR2d2(model=model))
            self.tasks.append(ta.StageJediCycle(model=model))
            self.tasks.append(ta.RenderJediObservations(model=model))
            self.tasks.append(ta.RunJediHofxExecutable(model=model))
            self.tasks.append(ta.EvaObservations(model=model))
            self.tasks.append(ta.SaveObsDiags(model=model))
            self.tasks.append(ta.CleanCycle(model=model))

# --------------------------------------------------------------------------------------------------
