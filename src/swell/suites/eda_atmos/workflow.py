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

            # logic tree:
            # prep (clone, stage, build, get bkg, get obs) -> SP1
            # -> mksi/observation + filter -> EDA_start
            # -> [ submit/wait for N member runs ]-> EDA_end
            # -> mean/variance + diffstate -> SP2 -> eva

            # Task triggers for: {{model_component}}
            # ------------------
            # Generate satellite channel records
            CloneGeosMksi-{{model_component}}[^] => GenerateObservingSystemRecords-{{model_component}}

            # Get observations
            {% if models[model_component]['cycling_varbc'] %}
            # Cycling VarBC is active, biases from the previous cycle will be used

            RunJediEdaExecutable-{{model_component}}[-PT6H] => GetObservations-{{model_component}}
            {% else %}

            # Cycling VarBC is inactive, static bias files will be used
            GetObsNotInR2d2-{{model_component}}: fail? => GetObservations-{{model_component}}
            {% endif %}

            # Perform staging that is cycle dependent
            StageJediCycle-{{model_component}}

            # Run Jedi variational executable
            BuildJediByLinking[^]? | BuildJedi[^]  => SP1-{{model_component}}
            CloneJedi[^] => StageJediCycle-{{model_component}}
            StageJediCycle-{{model_component}} => SP1-{{model_component}}
            GetEnsembleGeosExperiment-{{model_component}} => SP1-{{model_component}}
            GetObsNotInR2d2-{{model_component}}? | GetObservations-{{model_component}} => SP1-{{model_component}}
            SP1-{{model_component}} => GenerateObservingSystemRecords-{{model_component}}
            GenerateObservingSystemRecords-{{model_component}} => RenderJediObservations-{{model_component}}
            RenderJediObservations-{{model_component}} => RunJediObsfiltersExecutable-{{model_component}} => EDA_start-{{model_component}}

            {% if models[model_component]['ensemble_num_members'] is defined %}
            {% for i in range( 1, models[model_component]['ensemble_num_members'] + 1 ) %}
            EDA_start-{{model_component}} => RunJediEdaExecutable_mem{{i}}-{{model_component}} => EDA_end-{{model_component}}
            {% endfor %}
            {% endif %}

            # bkg/ana : mean/variance
            EDA_end-{{model_component}} => RunJediEnsembleMeanVariance-{{model_component}}
            RunJediEnsembleMeanVariance-{{model_component}} => RunJediDiffstates-{{model_component}} => SP2-{{model_component}}

            # CleanupEda directory
            SP2-{{model_component}} => CleanEda-{{model_component}}

            # EvaIncrement
            SP2-{{model_component}} => EvaIncrement-{{model_component}}

        {% endif %}
        {% endfor %}
        """
        {% endfor %}

# --------------------------------------------------------------------------------------------------

[runtime]

    # Task defaults
    # -------------
    {% for model_component in model_components %}
    # SP: Sync Point
    [[SP1-{{model_component}}]]
        script = true

    [[EDA_start-{{model_component}}]]
        script = true

    [[EDA_end-{{model_component}}]]
        script = true

    [[SP2-{{model_component}}]]
        script = true

    {% endfor %}
'''  # noqa

# --------------------------------------------------------------------------------------------------


@workflows.register('eda_atmos')
class Workflow_eda_atmos(CylcWorkflow):

    def get_workflow_string(self):
        workflow_str = self.default_header()

        workflow_str += template_string_jinja2(logger=self.logger,
                                               templated_string=template_str,
                                               dictionary_of_templates=self.experiment_dict,
                                               allow_unresolved=True)

        for task in self.tasks:
            workflow_str += task.runtime_string(self.experiment_dict,
                                                self.slurm_external)

        for model in self.experiment_dict['model_components']:
            for mem in range(1, self.experiment_dict['models'][model]['ensemble_num_members'] + 1):
                eda_task = ta.RunJediEdaExecutable(
                        scheduling_name=f'RunJediEdaExecutable_mem{mem}-{model}',
                        script=(f'swell task RunJediEdaExecutable -m {model}'
                                f' -d $datetime $config -imem {mem}'), model=model,
                        additional_values={'inherit': f'RunJediEdaExecutable-{model}'})

                workflow_str += eda_task.runtime_string(self.experiment_dict,
                                                        self.slurm_external)

        self.experiment_dict['stall_timeout'] = """\
        {% if environ.get('SWELL_CYLC_TIMEOUT') %}
        [[events]]
        stall timeout = {{environ['SWELL_CYLC_TIMEOUT']}}
        {% endif %}"""

        workflow_str = template_string_jinja2(logger=self.logger,
                                              templated_string=workflow_str,
                                              dictionary_of_templates=self.experiment_dict,
                                              allow_unresolved=True)

        return workflow_str

    def set_tasks(self) -> list:

        self.tasks.append(ta.root())
        self.tasks.append(ta.CloneJedi())
        self.tasks.append(ta.BuildJediByLinking())
        self.tasks.append(ta.BuildJedi())
        for model in self.experiment_dict['model_components']:
            self.tasks.append(ta.CloneGeosMksi(model=model))
            self.tasks.append(ta.GenerateObservingSystemRecords(model=model))
            self.tasks.append(ta.GetObsNotInR2d2(model=model))
            self.tasks.append(ta.StageJediCycle(model=model))
            self.tasks.append(ta.GetBackground(model=model))
            self.tasks.append(ta.GetBackgroundGeosExperiment(model=model))
            self.tasks.append(ta.GetEnsembleGeosExperiment(model=model))
            self.tasks.append(ta.GetObservations(model=model))
            self.tasks.append(ta.RenderJediObservations(model=model))
            self.tasks.append(ta.RunJediEdaExecutable(model=model))
            self.tasks.append(ta.RunJediObsfiltersExecutable(model=model))
            self.tasks.append(ta.RunJediEnsembleMeanVariance(model=model))
            self.tasks.append(ta.RunJediEdaExecutable(model=model))
            self.tasks.append(ta.RunJediDiffstates(model=model))
            self.tasks.append(ta.CleanEda(model=model))
            self.tasks.append(ta.EvaJediLog(model=model))
            self.tasks.append(ta.EvaIncrement(model=model))
            self.tasks.append(ta.EvaObservations(model=model))
            self.tasks.append(ta.SaveObsDiags(model=model))
            self.tasks.append(ta.CleanCycle(model=model))
            self.tasks.append(ta.CleanCycleSkipped(model=model))

# --------------------------------------------------------------------------------------------------
