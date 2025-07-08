# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.cylc_workflow import CylcWorkflow

# --------------------------------------------------------------------------------------------------

r1_template = """
# Triggers for non cycle time dependent tasks
# -------------------------------------------
# Clone JEDI source code
CloneJedi

# Build JEDI source code by linking
CloneJedi => BuildJediByLinking?

# If not able to link to build create the build
BuildJediByLinking:fail? => BuildJedi
"""

r1_model = """
# Stage JEDI static files
CloneJedi => StageJedi-{model_component}
"""

cycle_template = """
# Task triggers for: {model_component}
# ------------------
# Get background
GetBackground-{model_component}

# Get observations
GetObservations-{model_component}

# GenerateBClimatology, for ocean it is cycle dependent
GenerateBClimatologyByLinking-{model_component}:fail? =>
GenerateBClimatology-{model_component}

GetBackground-{model_component} => GenerateBClimatology-{model_component}

# Perform staging that is cycle dependent
StageJediCycle-{model_component}

# Run Jedi variational executable
BuildJediByLinking[^]? | BuildJedi[^]  => RunJediVariationalExecutable-{model_component}
StageJedi-{model_component}[^] => RunJediVariationalExecutable-{model_component}
StageJediCycle-{model_component} => RunJediVariationalExecutable-{model_component}
GetBackground-{model_component} => RunJediVariationalExecutable-{model_component}

GenerateBClimatologyByLinking-{model_component}? |
GenerateBClimatology-{model_component} =>
RunJediVariationalExecutable-{model_component}

GetObservations-{model_component} => RunJediVariationalExecutable-{model_component}

# EvaObservations
RunJediVariationalExecutable-{model_component} => EvaObservations-{model_component}

# EvaJediLog
RunJediVariationalExecutable-{model_component} => EvaJediLog-{model_component}

# EvaIncrement
RunJediVariationalExecutable-{model_component} => EvaIncrement-{model_component}

# Save observations
RunJediVariationalExecutable-{model_component} => SaveObsDiags-{model_component}

# Clean up large files
EvaObservations-{model_component} & SaveObsDiags-{model_component} =>
CleanCycle-{model_component}
"""

# --------------------------------------------------------------------------------------------------

class Workflow_3dvar(CylcWorkflow):
    def define_description(self):
        description = self.comment_block("""
        # Cylc suite for executing JEDI-based non-cycling variational data assimilation
        """)

        return description

    # --------------------------------------------------------------------------------------------------

    def define_graph_section(self):
        # Define the string of the graph section
        graph_str = ''

        # Define the string for the R1 (first non-cycling) section
        r1 = r1_template

        for model_component in self.experiment_dict['model_components']:
            r1 += r1_model.format(model_component=model_component)

        # Format the R1 cycle and add it to the graph
        graph_str += self.format_cycle('R1', r1)

        # Format the string for each cycle
        for model_component in self.experiment_dict['model_components']:
            if 'cycle_times' in self.experiment_dict['models'][model_component]:
                for cycle_time in self.experiment_dict['models'][model_component]['cycle_times']:
                    cycle_str = cycle_template.format(model_component=model_component)

            # Add the cycle string to the graph string
            graph_str += self.format_cycle(cycle_time, cycle_str)

        # Create the graph section
        graph_section = self.create_new_section('graph', graph_str)

        return graph_section

# --------------------------------------------------------------------------------------------------
