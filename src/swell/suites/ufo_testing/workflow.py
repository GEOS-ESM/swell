# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.cylc_workflow import CylcWorkflow

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
        r1 = """
            # Triggers for non cycle time dependent tasks
            # -------------------------------------------
            # Clone JEDI source code
            CloneJedi

            # Build JEDI source code by linking
            CloneJedi => BuildJediByLinking?

            # If not able to link to build create the build
            BuildJediByLinking:fail? => BuildJedi

            # Clone geos ana for generating observing system records
            CloneGeosMksi
            """

        # Format the R1 cycle and add it to the graph
        graph_str += self.format_cycle('R1', r1)

        # Format the string for each cycle
        for cycle_time in self.experiment_dict['cycle_times']:
            cycle_str = f"""

            # Generate satellite channel records
            CloneGeosMksi[^] => GenerateObservingSystemRecords

            # Convert bias correction to ioda
            GetGsiBc
            GetGsiBc => GsiBcToIoda
            BuildJediByLinking[^]? | BuildJedi[^]  => GsiBcToIoda

            # Convert ncdiags to ioda
            GetGsiNcdiag
            GetGsiNcdiag => GsiNcdiagToIoda
            BuildJediByLinking[^]? | BuildJedi[^]  => GsiNcdiagToIoda

            GetGeovals

            # Run Jedi hofx executable
            GenerateObservingSystemRecords => RunJediUfoTestsExecutable
            GsiNcdiagToIoda => RunJediUfoTestsExecutable
            GsiBcToIoda => RunJediUfoTestsExecutable
            GetGeovals => RunJediUfoTestsExecutable

            # EvaObservations
            RunJediUfoTestsExecutable => EvaObservations

            # Clean up large files
            EvaObservations => CleanCycle
            """

            # Add the cycle string to the graph string
            graph_str += self.format_cycle(cycle_time, cycle_str)

        # Create the graph section
        graph_section = self.create_new_section('graph', graph_str)

        return graph_section

# --------------------------------------------------------------------------------------------------
