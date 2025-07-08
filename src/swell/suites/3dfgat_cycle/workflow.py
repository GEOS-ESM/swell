# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.cylc_workflow import CylcWorkflow

# --------------------------------------------------------------------------------------------------


class Workflow_3dfgat_cycle(CylcWorkflow):
    def define_description(self):
        description = self.comment_block("""
        # Cylc suite for executing Geos forecast
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
            # Clone Geos source code
            CloneGeos

            # Clone JEDI source code
            CloneJedi

            # Build Geos source code by linking
            CloneGeos => BuildGeosByLinking?

            # Build JEDI source code by linking
            CloneJedi => BuildJediByLinking?

            # If not able to link to build create the build
            BuildGeosByLinking:fail? => BuildGeos

            # If not able to link to build create the build
            BuildJediByLinking:fail? => BuildJedi

            # Need first set of restarts to run model
            GetGeosRestart => PrepGeosRunDir

            # Model cannot run without code
            BuildGeosByLinking? | BuildGeos => RunGeosExecutable
            """

        for model_component in self.experiment_dict['model_components']:
            r1 += f"""
            # JEDI cannot run without code
            BuildJediByLinking? | BuildJedi => RunJediFgatExecutable-{model_component}

            # Stage JEDI static files
            CloneJedi => StageJedi-{model_component} => RunJediFgatExecutable-{model_component}
             """

        # Format the R1 cycle and add it to the graph
        graph_str += self.format_cycle('R1', r1)

        # Format the string for each cycle
        for model_component in self.experiment_dict['model_components']:
            if 'cycle_times' in self.experiment_dict['models'][model_component]:
                for cycle_time in self.experiment_dict['models'][model_component]['cycle_times']:
                    cycle_str = f"""
            # Model preperation
            # Run the forecast through two windows (need to output restarts at the end of the
            # first window and backgrounds for the second window)
            # MoveDaRestart-{model_component}[-P1D] => PrepGeosRunDir
            MoveDaRestart-{model_component}[-PT6H] => PrepGeosRunDir
            PrepGeosRunDir => RunGeosExecutable

            # Run the analysis
            # RunGeosExecutable => StageJediCycle-{model_component}
            RunGeosExecutable => LinkGeosOutput-{model_component}
            LinkGeosOutput-{model_component} => GenerateBClimatology-{model_component}

            # Data assimilation preperation
            GetObservations-{model_component}
            GenerateBClimatologyByLinking-{model_component} :fail? =>
            GenerateBClimatology-{model_component}

            LinkGeosOutput-{model_component} => RunJediFgatExecutable-{model_component}
            StageJediCycle-{model_component} => RunJediFgatExecutable-{model_component}
            GenerateBClimatologyByLinking-{model_component}? |
            GenerateBClimatology-{model_component} => RunJediFgatExecutable-{model_component}

            GetObservations-{model_component} => RunJediFgatExecutable-{model_component}

            # Run analysis diagnostics
            RunJediFgatExecutable-{model_component} => EvaObservations-{model_component}
            RunJediFgatExecutable-{model_component} => EvaJediLog-{model_component}
            EvaIncrement-{model_component} => PrepareAnalysis-{model_component}

            # Prepare analysis for next forecast
            RunJediFgatExecutable-{model_component} => EvaIncrement-{model_component}
            """
                    if 'cice6' in self.experiment_dict['models']['geos_marine']['marine_models']:
                        cycle_str += f"""
            PrepareAnalysis-{model_component} =>
            RunJediConvertStateSoca2ciceExecutable-{model_component}

            RunJediConvertStateSoca2ciceExecutable-{model_component} =>
            SaveRestart-{model_component}

            RunJediConvertStateSoca2ciceExecutable-{model_component} =>
            CleanCycle-{model_component}
            """
                    else:
                        cycle_str += f"""
            PrepareAnalysis-{model_component} => SaveRestart-{model_component}
            """

                    cycle_str += f"""
            # Move restart to next cycle
            SaveRestart-{model_component} => MoveDaRestart-{model_component}

            # Save analysis output
            # RunJediFgatExecutable-{model_component} => SaveAnalysis-{model_component}
            RunJediFgatExecutable-{model_component} => SaveObsDiags-{model_component}

            # Save model output
            # MoveBackground-{model_component} => StoreBackground-{model_component}

            # Remove Run Directory
            # MoveDaRestart-{model_component} & MoveBackground-{model_component} =>
            RemoveForecastDir

            MoveDaRestart-{model_component} => RemoveForecastDir

            # Clean up large files
            EvaObservations-{model_component} & EvaJediLog-{model_component} &
            EvaIncrement-{model_component} & SaveObsDiags-{model_component} =>
            CleanCycle-{model_component}
            """

            # Add the cycle string to the graph string
            graph_str += self.format_cycle(cycle_time, cycle_str)

        # Create the graph section
        graph_section = self.create_new_section('graph', graph_str)

        return graph_section

# --------------------------------------------------------------------------------------------------
