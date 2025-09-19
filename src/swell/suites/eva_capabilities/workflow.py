# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.cylc_workflow import CylcWorkflow

# --------------------------------------------------------------------------------------------------

r1_model = """
# Clone geos ana for generating observing system records
CloneGeosMksi-{model_component}
"""

cycle_template = """
GetNcdiags-{model_component}
CloneGeosMksi-{model_component}[^] => GenerateObservingSystemRecords-{model_component}
"""

r_final = """
GetNcdiags-{model_component} => EvaTimeseries-{model_component}
GenerateObservingSystemRecords-{model_component} => EvaTimeseries-{model_component}
EvaTimeseries-{model_component} => CleanCycle-{model_component}
"""

# --------------------------------------------------------------------------------------------------


class Workflow_eva_capabilities(CylcWorkflow):
    def define_description(self):
        description = self.comment_block("""
        # Cylc suite for executing geos_atmosphere ObsFilters tests
        """)

        return description

    # --------------------------------------------------------------------------------------------------

    def define_graph_section(self):
        # Define the string of the graph section
        graph_str = ''

        r1 = ''

        # Define the string for the R1 (first non-cycling) section
        for model in self.experiment_dict['models'].keys():
            r1 += r1_model.format(model_component=model)

        # Format the R1 cycle and add it to the graph
        graph_str += self.format_cycle('R1', r1)

        # Format the string for each cycle
        for model in self.experiment_dict['models'].keys():
            if 'cycle_times' in self.experiment_dict['models'][model].keys():
                for cycle_time in self.experiment_dict['models'][model]['cycle_times']:
                    cycle_str = cycle_template.format(model_component=model)
                    graph_str += self.format_cycle(cycle_time, cycle_str)

        cycle_str = ''

        # Format the final cycle
        for model in self.experiment_dict['models'].keys():
            cycle_str += r_final.format(model_component=model)
        graph_str += self.format_cycle('R1/$', cycle_str)

        # Create the graph section
        graph_section = self.create_new_section('graph', graph_str)

        return graph_section

# --------------------------------------------------------------------------------------------------
