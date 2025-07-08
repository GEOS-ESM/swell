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
# Clone geos ana for generating observing system records
CloneGeosMksi-{model_component}
"""

cycle_template_1 = """
# Task triggers for: {model_component}
# ------------------
# Generate satellite channel records
CloneGeosMksi-{model_component}[^] => GenerateObservingSystemRecords-{model_component}

# Get background, provide a way to get background directly from GEOS experiment
GetBackgroundGeosExperiment-{model_component} :fail? => GetBackground-{model_component}

# Get observations
"""

cycle_template_2 = """
# Cycling VarBC is active, biases from the previous cycle will be used

RunJediVariationalExecutable-{model_component}[-PT6H] => GetObservations-{model_component}
"""

cycle_template_3 = """
# Cycling VarBC is inactive, static bias files will be used
GetObservations-{model_component}
"""

cycling_template_4 = """
# Perform staging that is cycle dependent
StageJediCycle-{model_component}

# Run Jedi variational executable
BuildJediByLinking[^]? | BuildJedi[^]  => RunJediVariationalExecutable-{model_component}
CloneJedi[^] => StageJediCycle-{model_component}
StageJediCycle-{model_component} => RunJediVariationalExecutable-{model_component}
GetBackgroundGeosExperiment-{model_component}? | GetBackground-{model_component} =>
RunJediVariationalExecutable-{model_component}

GetObservations-{model_component} => RunJediVariationalExecutable-{model_component}
GenerateObservingSystemRecords-{model_component} => RunJediVariationalExecutable-{model_component}

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

class Workflow_3dfgat_atmos(CylcWorkflow):
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
                    cycle_str = cycle_template_1.format(model_component=model_component)

                    if self.experiment_dict['models'][model_component]['cycling_varbc']:
                        cycle_str += cycle_template_2.format(model_component=model_component)
                    else:
                        cycle_str += cycle_template_3.format(model_component=model_component)

                    cycle_str += cycling_template_4.format(model_component=model_component)

                    # Add the cycle string to the graph string
                    graph_str += self.format_cycle(cycle_time, cycle_str)

        # Create the graph section
        graph_section = self.create_new_section('graph', graph_str)

        return graph_section

# --------------------------------------------------------------------------------------------------
