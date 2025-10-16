# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.cylc_workflow import CylcWorkflow
from swell.tasks.task_runtimes import TaskRuntimes as tr

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
            # Get background
            GetBackground-{{model_component}}

            # Get observations
            GetObservations-{{model_component}}

            # GenerateBClimatology, for ocean it is cycle dependent
            GenerateBClimatologyByLinking-{{model_component}} :fail? => GenerateBClimatology-{{model_component}}
            GetBackground-{{model_component}} => GenerateBClimatology-{{model_component}}

            # Perform staging that is cycle dependent
            StageJediCycle-{{model_component}}

            # Run Jedi variational executable
            BuildJediByLinking[^]? | BuildJedi[^]  => RunJediVariationalExecutable-{{model_component}}
            StageJedi-{{model_component}}[^] => RunJediVariationalExecutable-{{model_component}}
            StageJediCycle-{{model_component}} => RunJediVariationalExecutable-{{model_component}}
            GetBackground-{{model_component}} => RunJediVariationalExecutable-{{model_component}}
            GenerateBClimatologyByLinking-{{model_component}}? | GenerateBClimatology-{{model_component}} => RunJediVariationalExecutable-{{model_component}}
            GetObservations-{{model_component}} => RunJediVariationalExecutable-{{model_component}}

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


class Workflow_3dvar(CylcWorkflow):

    def get_workflow_string(self):
        workflow_str = self.default_header()
        workflow_str += template_string_jinja2(logger=self.logger,
                                               templated_string=template_str,
                                               dictionary_of_templates=self.experiment_dict,
                                               allow_unresolved=True)
        
        for task_name, task in self.tasks().items():
            workflow_str += task.runtime_string(self.experiment_dict,
                                                self.slurm_external)

        return workflow_str
    
    def tasks(self) -> list:
        tasks = {}
        tasks['root'] = tr.root()
        tasks['CloneJedi'] = tr.CloneJedi()
        tasks['BuildJediByLinking'] = tr.BuildJediByLinking()
        tasks['BuildJedi'] = tr.BuildJedi()

        for model in self.experiment_dict['model_components']:
            tasks[f'StageJedi-{model}'] = tr.StageJedi(model=model)
            tasks[f'GetBackground-{model}'] = tr.GetBackground(model=model)
            tasks[f'GetObservations-{model}'] = tr.GetObservations(model=model)
            tasks[f'GenerateBClimatologyByLinking-{model}'] = tr.GenerateBClimatologyByLinking(model=model)
            tasks[f'GenerateBClimatology-{model}'] = tr.GenerateBClimatology(model=model)
            tasks[f'StageJediCycle-{model}'] = tr.StageJediCycle(model=model)
            tasks[f'GetBackground-{model}'] = tr.GetBackground(model=model)
            tasks[f'RunJediVariational-{model}'] = tr.RunJediVariationalExecutable(model=model)
            tasks[f'EvaObservations-{model}'] = tr.EvaObservations(model=model)
            tasks[f'EvaJediLog-{model}'] = tr.EvaJediLog(model=model)
            tasks[f'EvaIncrement-{model}'] = tr.EvaIncrement(model=model)
            tasks[f'SaveObsDiags-{model}'] = tr.SaveObsDiags(model=model)
            tasks[f'CleanCycle-{model}'] = tr.CleanCycle(model=model)
        
        return tasks

# --------------------------------------------------------------------------------------------------
