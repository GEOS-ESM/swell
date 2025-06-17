# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.cylc_workflow import CylcWorkflow

# --------------------------------------------------------------------------------------------------


class Workflow_geosadas(CylcWorkflow):
    def define_description(self):
        description = self.comment_block("""
        # Cylc suite for executing JEDI-based non-cycling variational data assimilation
        """)

        return description

    # --------------------------------------------------------------------------------------------------
    
    def define_scheduling_section(self):
        scheduling_dict = {'initial cycle point': '2020-12-15T00:00:00Z',
                           'final cycle point': '2020-12-15T00:00:00Z'}
        
        scheduling_section = self.create_new_section('scheduling', scheduling_dict)
        return scheduling_section

    # --------------------------------------------------------------------------------------------------

    def define_graph_section(self):
        # Define the string of the graph section
        graph_str = ''

        # Define the string for the R1 (first non-cycling) section
        r1 = """
            # Clone JEDI source code
            CloneJedi

            # Build JEDI source code by linking
            BuildJediByLinking?

            # Stage JEDI static files
            CloneJedi => StageJedi

            # Clone geos ana for generating observing system records
            CloneGeosMksi
            """

        # Format the R1 cycle and add it to the graph
        graph_str += self.format_cycle('R1', r1)

        # Format the string for each cycle
        for cycle_time in ['T00']:
            cycle_str = f"""
            # Generate satellite channel records
            CloneGeosMksi[^] => GenerateObservingSystemRecords

            # Get and convert bias correction coefficients
            GetGsiBc => GsiBcToIoda

            # Get and convert ncdiags
            GetGsiNcdiag => GsiNcdiagToIoda

            # Get background
            GetGeosAdasBackground

            # Run Jedi variational executable
            GenerateObservingSystemRecords => RunJediVariationalExecutable
            BuildJediByLinking[^]  => RunJediVariationalExecutable
            StageJedi[^] => RunJediVariationalExecutable
            GsiBcToIoda => RunJediVariationalExecutable
            GsiNcdiagToIoda => RunJediVariationalExecutable
            GetGeosAdasBackground => RunJediVariationalExecutable

            # Clean cycle
            RunJediVariationalExecutable => CleanCycle
            """
            graph_str += self.format_cycle(cycle_time, cycle_str)

        # Create the graph section
        graph_section = self.create_new_section('graph', graph_str)

        return graph_section

# --------------------------------------------------------------------------------------------------
