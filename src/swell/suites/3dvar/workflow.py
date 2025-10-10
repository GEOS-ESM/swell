# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.cylc_workflow import CylcWorkflow

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
'''

# --------------------------------------------------------------------------------------------------


class Workflow_3dvar(CylcWorkflow):

    def define_initial_workflow(self):
        workflow_str = self.default_header()
        workflow_str += template_string_jinja2(logger=self.logger,
                                               templated_string=template_str,
                                               dictionary_of_templates=self.experiment_dict,
                                               allow_unresolved=True)
        
        return workflow_str

# --------------------------------------------------------------------------------------------------
