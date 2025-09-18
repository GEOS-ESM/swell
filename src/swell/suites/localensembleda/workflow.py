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

# Perform staging that is cycle dependent
BuildJediByLinking[^]? | BuildJedi[^] => StageJediCycle-{model_component} => sync_point

GetObservations-{model_component} => sync_point

CloneGeosMksi-{model_component}[^] => GenerateObservingSystemRecords-{model_component} => sync_point

GetEnsembleGeosExperiment-{model_component} => sync_point

sync_point => RunJediObsfiltersExecutable-{{model_component}}
"""

cycle_template_2 = """
sync_point => RunJediObsfiltersExecutable-{{model_component}} => RunJediLocalEnsembleDaExecutable-{model_component}
"""

cycle_template_3 = """
sync_point => RunJediEnsembleMeanVariance-{model_component} =>
RunJediHofxEnsembleExecutable-{model_component}

RunJediHofxEnsembleExecutable-{model_component} =>
RunJediLocalEnsembleDaExecutable-{model_component}
"""

cycle_template_4 = """
# When strategy is parallel, only proceed if all RunJediHofxEnsembleExecutable completes
# successfully for each packet

# There is a need for a task to combine all hofx observations together, compute node preferred,
# put here as placeholder

# RunJediHofxEnsembleExecutable-{model_component}_pack{packet} =>
# RunEnsembleHofxCombiner-{model_component}

# RunEnsembleHofxCombiner-{model_component} =>
# RunJediLocalEnsembleDaExecutable-{model_component}

sync_point => RunJediHofxEnsembleExecutable-{model_component}_pack{packet}
RunJediHofxEnsembleExecutable-{model_component}_pack{packet} =>
RunJediLocalEnsembleDaExecutable-{model_component}
"""

cycle_template_5 = """
# EvaIncrement
RunJediLocalEnsembleDaExecutable-{model_component} => EvaIncrement-{model_component}

# EvaObservations
# RunJediLocalEnsembleDaExecutable-{model_component} => EvaObservations-{model_component}

# Save observations
# RunJediLocalEnsembleDaExecutable-{model_component} => SaveObsDiags-{model_component}

# Clean up large files
# EvaObservations-{{model_component}} & SaveObsDiags-{{model_component}} &
EvaIncrement-{{model_component}} => CleanCycle-{{model_component}}

"""

# --------------------------------------------------------------------------------------------------


class Workflow_localensembleda(CylcWorkflow):
    def define_description(self):
        description = self.comment_block("""
        # Cylc suite for executing JEDI-based h(x)
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

                    if self.experiment_dict['models'][model_component]['skip_ensemble_hofx']:
                        cycle_str += cycle_template_2.format(model_component=model_component)
                    else:
                        if self.experiment_dict['ensemble_hofx_strategy'] == 'serial':
                            cycle_str += cycle_template_3.format(model_component=model_component)
                        elif self.experiment_dict['ensemble_hofx_strategy'] == 'parallel':
                            for packet in range(self.experiment_dict['ensemble_hofx_packets']):
                                cycle_str += cycle_template_4.format(
                                        model_component=model_component, packet=packet)

                    cycle_str += cycle_template_5.format(model_component=model_component)

                    # Add the cycle string to the graph string
                    graph_str += self.format_cycle(cycle_time, cycle_str)

        # Create the graph section
        graph_section = self.create_new_section('graph', graph_str)

        return graph_section

# --------------------------------------------------------------------------------------------------
