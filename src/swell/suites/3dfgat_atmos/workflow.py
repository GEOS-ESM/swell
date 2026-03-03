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

# Cylc suite for executing JEDI-based non-cycling variational data assimilation

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
            {% if cycling_varbc %}
            # Cycling VarBC is active, biases from the previous cycle will be used

            RunJediVariationalExecutable-{{model_component}}[-PT6H] => GetObservations-{{model_component}}
            {% else %}

            # Cycling VarBC is inactive, static bias files will be used
            GetObservations-{{model_component}}
            {% endif %}

            # Perform staging that is cycle dependent
            StageJediCycle-{{model_component}}

            # Run Jedi variational executable
            BuildJediByLinking[^]? | BuildJedi[^]  => RunJediVariationalExecutable-{{model_component}}
            CloneJedi[^] => StageJediCycle-{{model_component}}
            StageJediCycle-{{model_component}} => RunJediVariationalExecutable-{{model_component}}
            GetBackgroundGeosExperiment-{{model_component}}? | GetBackground-{{model_component}} =>
            RunJediVariationalExecutable-{{model_component}}

            GetObsNotInR2d2-{{model_component}}: fail? => GetObservations-{{model_component}}

            GetObsNotInR2d2-{{model_component}}? | GetObservations-{{model_component}} => RenderJediObservations-{{model_component}}
            GenerateObservingSystemRecords-{{model_component}} => RunJediVariationalExecutable-{{model_component}}

            RenderJediObservations-{{model_component}} => RunJediVariationalExecutable-{{model_component}}


            # EvaObservations
            RunJediVariationalExecutable-{{model_component}} => EvaObservations-{{model_component}}

            # EvaJediLog
            RunJediVariationalExecutable-{{model_component}} => EvaJediLog-{{model_component}}

            # EvaIncrement
            RunJediVariationalExecutable-{{model_component}} => EvaIncrement-{{model_component}}

            # Save observations
            RunJediVariationalExecutable-{{model_component}} => SaveObsDiags-{{model_component}}

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


@workflows.register('3dfgat_atmos')
class Workflow_3dfgat_atmos(CylcWorkflow):

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

    def set_tasks(self) -> None:

        self.tasks.append(ta.root())
        self.tasks.append(ta.CloneJedi())
        self.tasks.append(ta.BuildJediByLinking())
        self.tasks.append(ta.BuildJedi())

        for model in self.experiment_dict['model_components']:
            self.tasks.append(ta.CloneGeosMksi(model=model))
            self.tasks.append(ta.StageJedi(model=model))
            self.tasks.append(ta.GetBackground(model=model))
            self.tasks.append(ta.GetObservations(model=model))
            self.tasks.append(ta.GenerateBClimatologyByLinking(model=model))
            self.tasks.append(ta.GenerateBClimatology(model=model))
            self.tasks.append(ta.GetObsNotInR2d2(model=model))
            self.tasks.append(ta.GetBackgroundGeosExperiment(model=model))
            self.tasks.append(ta.GenerateObservingSystemRecords(model=model))
            self.tasks.append(ta.StageJediCycle(model=model))
            self.tasks.append(ta.RunJediVariationalExecutable(model=model))
            self.tasks.append(ta.RenderJediObservations(model=model))
            self.tasks.append(ta.EvaObservations(model=model))
            self.tasks.append(ta.EvaJediLog(model=model))
            self.tasks.append(ta.EvaIncrement(model=model))
            self.tasks.append(ta.SaveObsDiags(model=model))
            self.tasks.append(ta.CleanCycle(model=model))

# --------------------------------------------------------------------------------------------------
