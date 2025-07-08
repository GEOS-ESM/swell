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
# Clone Geos source code
CloneGeos

# Build Geos source code by linking
CloneGeos => BuildGeosByLinking?

# If not able to link to build create the build
BuildGeosByLinking:fail? => BuildGeos

# Need first set of restarts to run model
GetGeosRestart => PrepGeosRunDir

# Get first set of restarts
BuildGeosByLinking? | BuildGeos  => RunGeosExecutable
"""

cycle_template = """
# Run Geos Executable
PrepGeosRunDir => RunGeosExecutable
MoveForecastRestart[-PT6H] => PrepGeosRunDir

# Move restart to next cycle
RunGeosExecutable => MoveForecastRestart

# Save restarts if requested
# MoveForecastRestart[-PT6H] => SaveRestart

# Remove Run Directory
MoveForecastRestart => RemoveForecastDir
"""

# --------------------------------------------------------------------------------------------------

class Workflow_forecast_geos(CylcWorkflow):
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

        # Format the R1 cycle and add it to the graph
        graph_str += self.format_cycle('R1', r1)

        # Format the string for each cycle
        for model in self.experiment_dict['models'].keys():
            if 'cycle_times' in self.experiment_dict['models'][model]['cycle_times']:
                for cycle_time in self.experiment_dict['models'][model]['cycle_times']:
                    cycle_str = cycle_template
                    graph_str += self.format_cycle(cycle_time, cycle_str)

        # Create the graph section
        graph_section = self.create_new_section('graph', graph_str)

        return graph_section

# --------------------------------------------------------------------------------------------------
