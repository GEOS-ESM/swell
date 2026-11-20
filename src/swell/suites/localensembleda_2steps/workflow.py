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
from swell.utilities.jinja2 import template_string_jinja2

# --------------------------------------------------------------------------------------------------

template_str = '''
# --------------------------------------------------------------------------------------------------

# Cylc suite for executing JEDI-based LocalEnsembleDA Algorithm

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

            # Get observations
            {% if models[model_component]['cycling_varbc'] %}
            # Cycling VarBC is active, biases from the previous cycle will be used

            RunJediEtkfSolver-{{model_component}}[-PT6H] => GetObservations-{{model_component}}
            {% else %}

            # Cycling VarBC is inactive, static bias files will be used
            fetch_obs-{{model_component}}
            {% endif %}

            # Perform staging that is cycle dependent
            StageJediCycle-{{model_component}}

            BuildJediByLinking[^]? | BuildJedi[^]  => SP1-{{model_component}}
            CloneJedi[^] => StageJediCycle-{{model_component}}
            StageJediCycle-{{model_component}} => SP1-{{model_component}}
            GetEnsembleGeosExperiment-{{model_component}} => SP1-{{model_component}}
            fetch_obs-{{model_component}} => SP1-{{model_component}}
            SP1-{{model_component}} => GenerateObservingSystemRecords-{{model_component}}
            GenerateObservingSystemRecords-{{model_component}} => RenderJediObservations-{{model_component}}
            RenderJediObservations-{{model_component}} => RunJediObsfiltersExecutable-{{model_component}}

            {% if models[model_component]['skip_ensemble_hofx'] %}
               RunJediObsfiltersExecutable-{{model_component}} => RunJediEtkfObserver-{{model_component}}
               RunJediEtkfObserver-{{model_component}} => RunJediEtkfSolver-{{model_component}}
            {% else %}
               # Run hofx for ensemble members according to strategy
               {% if models[model_component]['ensemble_hofx_strategy'] == 'serial' %}
                   SP1-{{model_component}} => RunJediEnsembleMeanVariance-{{model_component}} => RunJediHofxEnsembleExecutable-{{model_component}}
                   RunJediHofxEnsembleExecutable-{{model_component}} => RunJediLocalEnsembleDaExecutable-{{model_component}}

               {% elif models[model_component]['ensemble_hofx_strategy'] == 'parallel' %}
                   {% for packet in range(models[model_component]['ensemble_hofx_packets']) %}
                      # When strategy is parallel, only proceed if all RunJediHofxEnsembleExecutable completes successfully for each packet

                      # There is a need for a task to combine all hofx observations together, compute node preferred, put here as placeholder
                      # RunJediHofxEnsembleExecutable-{{model_component}}_pack{{packet}} => RunEnsembleHofxCombiner-{{model_component}}
                      # RunEnsembleHofxCombiner-{{model_component}} => RunJediLocalEnsembleDaExecutable-{{model_component}}

                      SP1-{{model_component}} => RunJediHofxEnsembleExecutable-{{model_component}}_pack{{packet}}
                      RunJediHofxEnsembleExecutable-{{model_component}}_pack{{packet}} => RunJediLocalEnsembleDaExecutable-{{model_component}}
                   {% endfor %}
               {% endif %}
            {% endif %}


            # EvaIncrement
            RunJediEtkfSolver-{{model_component}} => EvaIncrement-{{model_component}}

            # EvaObservations
            RunJediEtkfSolver-{{model_component}} => EvaObservations-{{model_component}}

            # Save observations
            # RunJediEtkfSolver-{{model_component}} => SaveObsDiags-{{model_component}}

            # Clean up large files
            # EvaObservations-{{model_component}} & SaveObsDiags-{{model_component}} &
            EvaIncrement-{{model_component}} => CleanCycle-{{model_component}}

        {% endif %}
        {% endfor %}
        """
        {% endfor %}

# --------------------------------------------------------------------------------------------------

[runtime]
    {% for model_component in model_components %}
    # Task defaults
    # -------------
    # SP: Sync Point
    [[SP1-{{model_component}}]]
        script = true

    {% endfor %}
'''  # noqa

# --------------------------------------------------------------------------------------------------


@workflows.register('localensembleda_2steps')
class Workflow_localensembleda_2steps(CylcWorkflow):

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
            if self.experiment_dict['models'][model]['ensemble_hofx_strategy'] == 'parallel':
                for packet in range(self.experiment_dict['models'][model]['ensemble_hofx_packets']):
                    hofx_task = ta.RunJediHofxEnsembleExecutable(
                            scheduling_name=f'RunJediHofxExecutable_pack{packet}',
                            script=(f'swell task RunJediHofxEnsembleExecutable -m {model}'
                                    f' -d $datetime $config -p {packet}'), model=model)

                    workflow_str += hofx_task.runtime_string(self.experiment_dict,
                                                             self.slurm_external)

        self.experiment_dict['stall_timeout'] = """\
        {% if environ.get('SWELL_CYLC_TIMEOUT') %}
        [[events]]
        stall timeout = {{environ['SWELL_CYLC_TIMEOUT']}}
        {% endif %}"""

        workflow_str = template_string_jinja2(self.logger, workflow_str, self.experiment_dict, True)

        return workflow_str

    def set_tasks(self) -> list:

        self.tasks.append(ta.root())
        self.tasks.append(ta.CloneJedi())
        self.tasks.append(ta.BuildJedi())
        self.tasks.append(ta.BuildJediByLinking())

        for model in self.experiment_dict['model_components']:
            self.tasks.append(ta.CloneGeosMksi(model=model))
            self.tasks.append(ta.StageJediCycle(model=model))
            if self.experiment_dict['fetch_from_r2d2']:
                self.tasks.append(ta.GetObservations(model=model, scheduling_name=f'fetch_obs-{model}'))
            else:
                self.tasks.append(ta.GetObsNotInR2d2(model=model, scheduling_name=f'fetch_obs-{model}'))
            self.tasks.append(ta.GetBackground(model=model))
            self.tasks.append(ta.GenerateObservingSystemRecords(model=model))
            self.tasks.append(ta.GetEnsembleGeosExperiment(model=model))
            self.tasks.append(ta.sync_point(model=model))
            self.tasks.append(ta.RenderJediObservations(model=model))
            self.tasks.append(ta.RunJediObsfiltersExecutable(model=model))
            self.tasks.append(ta.RunJediLocalEnsembleDaExecutable(model=model))
            self.tasks.append(ta.RunJediEnsembleMeanVariance(model=model))
            self.tasks.append(ta.RunJediEtkfObserver(model=model))
            self.tasks.append(ta.RunJediEtkfSolver(model=model))
            if not self.experiment_dict['models'][model]['skip_ensemble_hofx']:
                self.tasks.append(ta.RunJediHofxEnsembleExecutable(model=model))
            self.tasks.append(ta.EvaIncrement(model=model))
            self.tasks.append(ta.EvaObservations(model=model))
            self.tasks.append(ta.SaveObsDiags(model=model))
            self.tasks.append(ta.CleanCycle(model=model))
            self.tasks.append(ta.CleanCycleSkipped(model=model))

# --------------------------------------------------------------------------------------------------
