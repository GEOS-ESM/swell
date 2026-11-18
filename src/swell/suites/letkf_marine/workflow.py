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

# Cylc suite for executing JEDI-based LocalEnsembleDA Algorithm (Marine)

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
            # Stage JEDI static files
            CloneJedi => StageJedi-{{model_component}}
            {% endfor %}
        """

        {% for cycle_time in cycle_times %}
        {{cycle_time.cycle_time}} = """
        {% for model_component in model_components %}
        {% if cycle_time[model_component] %}
            # Task triggers for: {{model_component}}
            # ------------------

            # Perform staging that is cycle dependent
            BuildJediByLinking[^]? | BuildJedi[^] => StageJediCycle-{{model_component}}

            # Get background and ensemble geos experiment files
            GetObservations-{{model_component}} => RenderJediObservations-{{model_component}}

            StageJedi-{{model_component}}[^] & StageJediCycle-{{model_component}} & RenderJediObservations-{{model_component}} & GetEnsemble-{{model_component}} => RunJediObsfiltersExecutable-{{model_component}}

            {% if models[model_component]['skip_ensemble_hofx'] %}
               RunJediObsfiltersExecutable-{{model_component}} => RunJediLocalEnsembleDaExecutable-{{model_component}}
            {% else %}
               # Run hofx for ensemble members according to strategy
               {% if models[model_component]['ensemble_hofx_strategy'] == 'serial' %}
                   RunJediObsfiltersExecutable-{{model_component}} => RunJediEnsembleMeanVariance-{{model_component}} => RunJediHofxEnsembleExecutable-{{model_component}}
                   RunJediHofxEnsembleExecutable-{{model_component}} => RunJediLocalEnsembleDaExecutable-{{model_component}}

               {% elif models[model_component]['ensemble_hofx_strategy'] == 'parallel' %}
                   {% for packet in range(models[model_component]['ensemble_hofx_packets']) %}
                      RunJediObsfiltersExecutable-{{model_component}} => RunJediHofxEnsembleExecutable-{{model_component}}_pack{{packet}}
                      RunJediHofxEnsembleExecutable-{{model_component}}_pack{{packet}} => RunJediLocalEnsembleDaExecutable-{{model_component}}
                   {% endfor %}
               {% endif %}
            {% endif %}


            # EvaIncrement
            RunJediLocalEnsembleDaExecutable-{{model_component}} => EvaIncrement-{{model_component}}

            # Clean up large files
            EvaIncrement-{{model_component}} => CleanCycle-{{model_component}}

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


@workflows.register('letkf_marine')
class Workflow_letkf_marine(CylcWorkflow):

    def get_workflow_string(self):
        workflow_str = self.default_header()

        workflow_str += template_string_jinja2(logger=self.logger,
                                               templated_string=template_str,
                                               dictionary_of_templates=self.experiment_dict,
                                               allow_unresolved=True)

        for task in self.tasks:
            workflow_str += task.runtime_string(self.experiment_dict,
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
            self.tasks.append(ta.StageJedi(model=model))
            self.tasks.append(ta.StageJediCycle(model=model))
            self.tasks.append(ta.GetBackground(model=model))
            self.tasks.append(ta.GetEnsemble(model=model))
            self.tasks.append(ta.GetObservations(model=model))
            self.tasks.append(ta.RenderJediObservations(model=model))
            self.tasks.append(ta.RunJediObsfiltersExecutable(model=model))
            self.tasks.append(ta.RunJediEnsembleMeanVariance(model=model))
            self.tasks.append(ta.RunJediHofxEnsembleExecutable(model=model))
            self.tasks.append(ta.RunJediLocalEnsembleDaExecutable(model=model))
            self.tasks.append(ta.EvaIncrement(model=model))
            self.tasks.append(ta.SaveObsDiags(model=model))
            self.tasks.append(ta.CleanCycle(model=model))
            self.tasks.append(ta.CleanCycleSkipped(model=model))

# --------------------------------------------------------------------------------------------------
