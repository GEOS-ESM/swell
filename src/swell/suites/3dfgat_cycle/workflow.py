# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.cylc_workflow import CylcWorkflow
from swell.tasks.task_attributes import TaskAttributes as ta

# --------------------------------------------------------------------------------------------------

template_str = '''
# --------------------------------------------------------------------------------------------------

# Cylc suite for executing Geos forecast

# --------------------------------------------------------------------------------------------------

[scheduler]
    UTC mode = True
    allow implicit tasks = False

# --------------------------------------------------------------------------------------------------

[scheduling]

    initial cycle point = {{start_cycle_point}}
    final cycle point = {{final_cycle_point}}
    runahead limit = {{runahead_limit}}

    [[graph]]
        R1 = """
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

            {% for model_component in model_components %}

            # JEDI cannot run without code
            BuildJediByLinking? | BuildJedi => RunJediFgatExecutable-{{model_component}}

            # Stage JEDI static files
            CloneJedi => StageJedi-{{model_component}} => RunJediFgatExecutable-{{model_component}}

            {% endfor %}
        """

        {% for cycle_time in cycle_times %}
        {{cycle_time.cycle_time}} = """
        {% for model_component in model_components %}

            # Model preperation
            # Run the forecast through two windows (need to output restarts at the end of the
            # first window and backgrounds for the second window)
            MoveDaRestart-{{model_component}}[-{{models[model_component]["window_length"]}}] => PrepGeosRunDir
            PrepGeosRunDir => RunGeosExecutable

            # Run the analysis
            # RunGeosExecutable => StageJediCycle-{{model_component}}
            RunGeosExecutable => LinkGeosOutput-{{model_component}}
            LinkGeosOutput-{{model_component}} => GenerateBClimatology-{{model_component}}

            # Data assimilation preperation
            GetObservations-{{model_component}}
            GenerateBClimatologyByLinking-{{model_component}} :fail? => GenerateBClimatology-{{model_component}}

            LinkGeosOutput-{{model_component}} => RunJediFgatExecutable-{{model_component}}
            StageJediCycle-{{model_component}} => RunJediFgatExecutable-{{model_component}}
            GenerateBClimatologyByLinking-{{model_component}}? | GenerateBClimatology-{{model_component}} => RunJediFgatExecutable-{{model_component}}
            GetObservations-{{model_component}} => RunJediFgatExecutable-{{model_component}}

            # Run analysis diagnostics
            RunJediFgatExecutable-{{model_component}} => EvaObservations-{{model_component}}
            RunJediFgatExecutable-{{model_component}} => EvaJediLog-{{model_component}}
            EvaIncrement-{{model_component}} => PrepareAnalysis-{{model_component}}

            # Prepare analysis for next forecast
            RunJediFgatExecutable-{{model_component}} => EvaIncrement-{{model_component}}
            {% if 'cice6' in models[model_component]["marine_models"] %}
            PrepareAnalysis-{{model_component}} => RunJediConvertStateSoca2ciceExecutable-{{model_component}}
            RunJediConvertStateSoca2ciceExecutable-{{model_component}} => SaveRestart-{{model_component}}
            RunJediConvertStateSoca2ciceExecutable-{{model_component}} => CleanCycle-{{model_component}}
            {% else %}
            PrepareAnalysis-{{model_component}} => SaveRestart-{{model_component}}
            {% endif %}

            # Move restart to next cycle
            SaveRestart-{{model_component}} => MoveDaRestart-{{model_component}}

            # Save analysis output
            # RunJediFgatExecutable-{{model_component}} => SaveAnalysis-{{model_component}}
            RunJediFgatExecutable-{{model_component}} => SaveObsDiags-{{model_component}}

            # Save model output
            # MoveBackground-{{model_component}} => StoreBackground-{{model_component}}

            # Remove Run Directory
            # MoveDaRestart-{{model_component}} & MoveBackground-{{model_component}} => RemoveForecastDir
            MoveDaRestart-{{model_component}} => RemoveForecastDir

            # Clean up large files
            EvaObservations-{{model_component}} & EvaJediLog-{{model_component}} & EvaIncrement-{{model_component}} & SaveObsDiags-{{model_component}} =>
            CleanCycle-{{model_component}}
        {% endfor %}
        """
        {% endfor %}
# --------------------------------------------------------------------------------------------------

[runtime]

    # Task defaults
    # -------------

'''  # noqa

# --------------------------------------------------------------------------------------------------


class Workflow_3dfgat_cycle(CylcWorkflow):

    def get_workflow_string(self):
        workflow_str = self.default_header()
        workflow_str += template_string_jinja2(logger=self.logger,
                                               templated_string=template_str,
                                               dictionary_of_templates=self.experiment_dict,
                                               allow_unresolved=True)

        for task in self.tasks():
            workflow_str += task.runtime_string(self.experiment_dict,
                                                self.slurm_external)

        return workflow_str

    def tasks(self) -> list:
        tasks = []
        tasks.append(ta.root())
        tasks.append(ta.CloneJedi())
        tasks.append(ta.CloneGeos())
        tasks.append(ta.BuildJediByLinking())
        tasks.append(ta.BuildJedi())
        tasks.append(ta.BuildGeos())
        tasks.append(ta.BuildGeosByLinking())

        tasks.append(ta.GetGeosRestart())
        tasks.append(ta.PrepGeosRunDir())
        tasks.append(ta.RunGeosExecutable())

        for model in self.experiment_dict['model_components']:
            tasks.append(ta.RunJediFgatExecutable(model=model))
            tasks.append(ta.StageJedi(model=model))
            tasks.append(ta.StageJediCycle(model=model))
            tasks.append(ta.MoveDaRestart(model=model))
            tasks.append(ta.LinkGeosOutput(model=model))
            tasks.append(ta.GenerateBClimatology(model=model))
            tasks.append(ta.GenerateBClimatologyByLinking(model=model))
            tasks.append(ta.GetObservations(model=model))
            tasks.append(ta.EvaObservations(model=model))
            tasks.append(ta.EvaJediLog(model=model))
            tasks.append(ta.EvaIncrement(model=model))
            tasks.append(ta.PrepareAnalysis(model=model))
            tasks.append(ta.RunJediConvertStateSoca2ciceExecutable(model=model))
            tasks.append(ta.SaveRestart(model=model))
            tasks.append(ta.CleanCycle(model=model))
            tasks.append(ta.PrepareAnalysis(model=model))
            tasks.append(ta.RemoveForecastDir(model=model))
            tasks.append(ta.SaveObsDiags(model=model))

        return tasks


# --------------------------------------------------------------------------------------------------
