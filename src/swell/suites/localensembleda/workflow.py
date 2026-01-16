# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.jinja2 import template_string_jinja2
from swell.suites.base.cylc_workflow import CylcWorkflow
from swell.tasks.base.task_attributes import task_attributes as ta

# --------------------------------------------------------------------------------------------------

template_str = '''

# --------------------------------------------------------------------------------------------------

# Cylc suite for executing JEDI-based LocalEnsembleDA Algorithm

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

            # Perform staging that is cycle dependent
            BuildJediByLinking[^]? | BuildJedi[^] => StageJediCycle-{{model_component}} => sync_point

            GetObsNotInR2d2-{{model_component}}: fail? => GetObservations-{{model_component}}

            GetObsNotInR2d2-{{model_component}}? | GetObservations-{{model_component}} => RenderJediObservations-{{model_component}}
            
            RenderJediObservations-{{model_component}} => sync_point

            CloneGeosMksi-{{model_component}}[^] => GenerateObservingSystemRecords-{{model_component}} => sync_point

            GetEnsembleGeosExperiment-{{model_component}} => sync_point

            sync_point => RunJediObsfiltersExecutable-{{model_component}}
            {% if skip_ensemble_hofx %}
               sync_point => RunJediObsfiltersExecutable-{{model_component}} => RunJediLocalEnsembleDaExecutable-{{model_component}}
            {% else %}
               # Run hofx for ensemble members according to strategy
               {% if ensemble_hofx_strategy == 'serial' %}
                   sync_point => RunJediEnsembleMeanVariance-{{model_component}} => RunJediHofxEnsembleExecutable-{{model_component}}
                   RunJediHofxEnsembleExecutable-{{model_component}} => RunJediLocalEnsembleDaExecutable-{{model_component}}

               {% elif ensemble_hofx_strategy == 'parallel' %}
                   {% for packet in range(ensemble_hofx_packets) %}
                      # When strategy is parallel, only proceed if all RunJediHofxEnsembleExecutable completes successfully for each packet

                      # There is a need for a task to combine all hofx observations together, compute node preferred, put here as placeholder
                      # RunJediHofxEnsembleExecutable-{{model_component}}_pack{{packet}} => RunEnsembleHofxCombiner-{{model_component}}
                      # RunEnsembleHofxCombiner-{{model_component}} => RunJediLocalEnsembleDaExecutable-{{model_component}}

                      sync_point => RunJediHofxEnsembleExecutable-{{model_component}}_pack{{packet}}
                      RunJediHofxEnsembleExecutable-{{model_component}}_pack{{packet}} => RunJediLocalEnsembleDaExecutable-{{model_component}}
                   {% endfor %}
               {% endif %}
            {% endif %}


            # EvaIncrement
            RunJediLocalEnsembleDaExecutable-{{model_component}} => EvaIncrement-{{model_component}}

            # EvaObservations
            # RunJediLocalEnsembleDaExecutable-{{model_component}} => EvaObservations-{{model_component}}

            # Save observations
            # RunJediLocalEnsembleDaExecutable-{{model_component}} => SaveObsDiags-{{model_component}}

            # Clean up large files
            # EvaObservations-{{model_component}} & SaveObsDiags-{{model_component}} &
            EvaIncrement-{{model_component}} => CleanCycle-{{model_component}}

        {% endif %}
        {% endfor %}
        """
        {% endfor %}

[runtime]

    # Task defaults
    # -------------

'''  # noqa

# --------------------------------------------------------------------------------------------------


class Workflow_localensembleda(CylcWorkflow):

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

        for model in self.experiment_dict['model_components']:
            self.tasks.append(ta.CloneGeosMksi(model=model))
            self.tasks.append(ta.StageJediCycle(model=model))
            self.tasks.append(ta.GetObsNotInR2d2(model=model))
            self.tasks.append(ta.GetObservations(model=model))
            self.tasks.append(ta.GenerateObservingSystemRecords(model=model))
            self.tasks.append(ta.GetEnsembleGeosExperiment(model=model))
            self.tasks.append(ta.sync_point(model=model))
            self.tasks.append(ta.RenderJediObservations(model=model))
            self.tasks.append(ta.RunJediObsfiltersExecutable(model=model))
            self.tasks.append(ta.RunJediLocalEnsembleDaExecutable(model=model))
            self.tasks.append(ta.RunJediEnsembleMeanVariance(model=model))
            self.tasks.append(ta.RunJediHofxEnsembleExecutable(model=model))
            self.tasks.append(ta.EvaIncrement(model=model))
            self.tasks.append(ta.EvaObservations(model=model))
            self.tasks.append(ta.SaveObsDiags(model=model))
            self.tasks.append(ta.CleanCycle(model=model))

# --------------------------------------------------------------------------------------------------
