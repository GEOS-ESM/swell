# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.cylc_workflow import CylcWorkflow

# --------------------------------------------------------------------------------------------------

class Workflow_3dvar(CylcWorkflow):
    def define_description(self):
        description = """
        # Cylc suite for executing JEDI-based non-cycling variational data assimilation
        """

        return description
    
    def define_graph_section(self):
        r1 = """
            # Triggers for non cycle time dependent tasks
            # -------------------------------------------
            # Clone JEDI source code
            CloneJedi

            # Build JEDI source code by linking
            CloneJedi => BuildJediByLinking?

            # If not able to link to build create the build
            BuildJediByLinking:fail? => BuildJedi
            """
        
        for model_component in self.experiment_dict['model_components']:
            r1 += """

            # Stage JEDI static files
            CloneJedi => StageJedi-{model_component}
             """.format(model_component=model_component)

        graph_str += self.format_cycle('R1', r1)

        for model_component in self.experiment_dict['model_components']:
            if 'cycle_times' in self.experiment_dict[model_component]:
                for cycle_time in self.experiment_dict[model_component]['cycle_times']:
                    cycle_str = """
            # Task triggers for: {model_component}
            # ------------------
            # Get background
            GetBackground-{model_component}

            # Get observations
            GetObservations-{model_component}

            # GenerateBClimatology, for ocean it is cycle dependent
            GenerateBClimatologyByLinking-{model_component} :fail? => GenerateBClimatology-{model_component}
            GetBackground-{model_component} => GenerateBClimatology-{model_component}

            # Perform staging that is cycle dependent
            StageJediCycle-{model_component}

            # Run Jedi variational executable
            BuildJediByLinking[^]? | BuildJedi[^]  => RunJediVariationalExecutable-{model_component}
            StageJedi-{model_component}[^] => RunJediVariationalExecutable-{model_component}
            StageJediCycle-{model_component} => RunJediVariationalExecutable-{model_component}
            GetBackground-{model_component} => RunJediVariationalExecutable-{model_component}
            GenerateBClimatologyByLinking-{model_component}? | GenerateBClimatology-{model_component} => RunJediVariationalExecutable-{model_component}
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

            cycle_str = cycle_str.format(model_component=model_component)
                    
            graph_str += self.format_cycle(cycle_time, cycle_str)

        return self.create_new_section('graph', graph_str)
    
# --------------------------------------------------------------------------------------------------