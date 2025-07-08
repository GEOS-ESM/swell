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
# Generate satellite channel records
CloneGeosMksi-{model_component}[^] => GenerateObservingSystemRecords-{model_component}

# Convert bias correction to ioda
GetGsiBc-{model_component}
GetGsiBc-{model_component} => GsiBcToIoda-{model_component}
BuildJediByLinking[^]? | BuildJedi[^]  => GsiBcToIoda-{model_component}

# Convert ncdiags to ioda
GetGsiNcdiag-{model_component}
GetGsiNcdiag-{model_component} => GsiNcdiagToIoda-{model_component}
BuildJediByLinking[^]? | BuildJedi[^]  => GsiNcdiagToIoda-{model_component}

GetGeovals-{model_component}

# Run Jedi hofx executable
GenerateObservingSystemRecords-{model_component} => RunJediUfoTestsExecutable-{model_component}
GsiNcdiagToIoda-{model_component} => RunJediUfoTestsExecutable-{model_component}
GsiBcToIoda-{model_component} => RunJediUfoTestsExecutable-{model_component}
GetGeovals-{model_component} => RunJediUfoTestsExecutable-{model_component}

# EvaObservations
RunJediUfoTestsExecutable-{model_component} => EvaObservations-{model_component}

# Clean up large files
EvaObservations-{model_component} => CleanCycle-{model_component}
"""

# --------------------------------------------------------------------------------------------------


class Workflow_ufo_testing(CylcWorkflow):
    def define_description(self):
        description = self.comment_block("""
        # Cylc suite for executing geos_atmosphere ObsFilters tests
        """)

        return description

    # --------------------------------------------------------------------------------------------------

    def define_graph_section(self):
        # Define the string of the graph section
        graph_str = ''

        # Define the string for the R1 (first non-cycling) section
        r1 = r1_template

        for model_component in self.experiment_dict['models']:
            r1 += r1_model.format(model_component=model_component)

        # Format the R1 cycle and add it to the graph
        graph_str += self.format_cycle('R1', r1)

        # Format the string for each cycle
        for model_component in self.experiment_dict['models']:
            if 'cycle_times' in self.experiment_dict['models'][model_component].keys():
                for cycle_time in self.experiment_dict['models'][model_component]['cycle_times']:
                    cycle_str = cycle_template_1.format(model_component=model_component)

                    # Add the cycle string to the graph string
                    graph_str += self.format_cycle(cycle_time, cycle_str)

        # Create the graph section
        graph_section = self.create_new_section('graph', graph_str)

        return graph_section

# --------------------------------------------------------------------------------------------------
