# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.jinja2 import template_string_jinja2
from swell.suites.base.cylc_workflow import CylcWorkflow
from swell.tasks.base.task_attributes import task_attributes as ta
from swell.suites.base.suite_attributes import workflows

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
            GetCoupledGeosRestart => PrepCoupledGeosRunDir

            # Model cannot run without code
            BuildGeosByLinking? | BuildGeos => RunGeos

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
            MoveDaRestart-{{model_component}}[-{{models[model_component]["window_length"]}}] => PrepCoupledGeosRunDir
            PrepCoupledGeosRunDir => RunGeos

            # Run the analysis
            RunGeos => LinkCoupledGeosOutput-{{model_component}}
            LinkCoupledGeosOutput-{{model_component}} => GenerateBClimatology-{{model_component}}

            # Data assimilation preperation
            GetObservations-{{model_component}} => RenderJediObservations-{{model_component}}
            RenderJediObservations-{{model_component}} => RunJediFgatExecutable-{{model_component}}

            LinkCoupledGeosOutput-{{model_component}} => RunJediFgatExecutable-{{model_component}}
            StageJediCycle-{{model_component}} => RunJediFgatExecutable-{{model_component}}
            GenerateBClimatology-{{model_component}} => RunJediFgatExecutable-{{model_component}}
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

            # Move restart to next cycle and then erase current forecast folder
            SaveRestart-{{model_component}} => MoveDaRestart-{{model_component}} => CleanCycle-{{model_component}}

            {% if not skip_r2d2 %}
            # Save analysis output
            # RunJediFgatExecutable-{{model_component}} => SaveAnalysis-{{model_component}}
            RunJediFgatExecutable-{{model_component}} => SaveObsDiags-{{model_component}} => CleanCycle-{{model_component}}
            {% endif %}

            # Save model output
            # MoveBackground-{{model_component}} => StoreBackground-{{model_component}}

            # Clean up large files
            EvaObservations-{{model_component}} & EvaJediLog-{{model_component}} & EvaIncrement-{{model_component}} =>
            CleanCycle-{{model_component}}
        {% endfor %}
        """
        {% endfor %}

# --------------------------------------------------------------------------------------------------

[runtime]

    # Task defaults
    # -------------

<<<<<<<< HEAD:src/swell/suites/3dfgat_marine_cycle/workflow.py
'''  # noqa

# --------------------------------------------------------------------------------------------------


@workflows.register('3dfgat_cycle')
class Workflow_3dfgat_cycle(CylcWorkflow):

    def get_workflow_string(self):
        workflow_str = self.default_header()
        workflow_str += template_string_jinja2(logger=self.logger,
                                               templated_string=template_str,
                                               dictionary_of_templates=self.experiment_dict,
                                               allow_unresolved=True)

        for task in self.tasks:
            workflow_str += task.runtime_string(self.experiment_dict,
                                                self.slurm_external)

        return workflow_str

    def set_tasks(self) -> None:

        self.tasks.append(ta.root())
        self.tasks.append(ta.CloneJedi())
        self.tasks.append(ta.CloneGeos())
        self.tasks.append(ta.BuildJediByLinking())
        self.tasks.append(ta.BuildJedi())
        self.tasks.append(ta.BuildGeos())
        self.tasks.append(ta.BuildGeosByLinking())

        self.tasks.append(ta.GetGeosRestart())
        self.tasks.append(ta.PrepGeosRunDir())
        self.tasks.append(ta.RunGeosExecutable())

        for model in self.experiment_dict['model_components']:
            self.tasks.append(ta.RunJediFgatExecutable(model=model))
            self.tasks.append(ta.StageJedi(model=model))
            self.tasks.append(ta.StageJediCycle(model=model))
            self.tasks.append(ta.MoveDaRestart(model=model))
            self.tasks.append(ta.LinkGeosOutput(model=model))
            self.tasks.append(ta.GenerateBClimatology(model=model))
            self.tasks.append(ta.GetObservations(model=model))
            self.tasks.append(ta.EvaObservations(model=model))
            self.tasks.append(ta.EvaJediLog(model=model))
            self.tasks.append(ta.EvaIncrement(model=model))
            self.tasks.append(ta.PrepareAnalysis(model=model))
            self.tasks.append(ta.RenderJediObservations(model=model))
            self.tasks.append(ta.RunJediConvertStateSoca2ciceExecutable(model=model))
            self.tasks.append(ta.SaveRestart(model=model))
            self.tasks.append(ta.CleanCycle(model=model))
            self.tasks.append(ta.PrepareAnalysis(model=model))
            self.tasks.append(ta.RemoveForecastDir(model=model))
            self.tasks.append(ta.SaveObsDiags(model=model))
========
        [[[environment]]]
            datetime = $CYLC_TASK_CYCLE_POINT
            config   = $CYLC_SUITE_DEF_PATH/experiment.yaml

    # Tasks
    # -----
    [[CloneGeos]]
        script = "swell task CloneGeos $config"

    [[BuildGeosByLinking]]
        script = "swell task BuildGeosByLinking $config"

    [[BuildGeos]]
        script = "swell task BuildGeos $config"
        platform = {{platform}}
        execution time limit = {{scheduling["BuildGeos"]["execution_time_limit"]}}
        [[[directives]]]
        {%- for key, value in scheduling["BuildGeos"]["directives"]["all"].items() %}
            --{{key}} = {{value}}
        {%- endfor %}

    [[CloneJedi]]
        script = "swell task CloneJedi $config"

    [[BuildJediByLinking]]
        script = "swell task BuildJediByLinking $config"

    [[BuildJedi]]
        script = "swell task BuildJedi $config"
        platform = {{platform}}
        execution time limit = {{scheduling["BuildJedi"]["execution_time_limit"]}}
        [[[directives]]]
        {%- for key, value in scheduling["BuildJedi"]["directives"]["all"].items() %}
            --{{key}} = {{value}}
        {%- endfor %}

    [[RunGeos]]
        script = "{{experiment_path}}/GEOSgcm/forecast/gcm_run.j"
        platform = {{platform}}
        [[[directives]]]
        {%- for key, value in scheduling["RunGeos"]["directives"]["all"].items() %}
            --{{key}} = {{value}}
        {%- endfor %}

    [[PrepCoupledGeosRunDir]]
        script = "swell task PrepCoupledGeosRunDir $config -d $datetime"

    [[GetCoupledGeosRestart]]
        script = "swell task GetCoupledGeosRestart $config -d $datetime"

    {% for model_component in model_components %}

    [[LinkCoupledGeosOutput-{{model_component}}]]
        script = "swell task LinkCoupledGeosOutput $config -d $datetime -m {{model_component}}"

    [[MoveDaRestart-{{model_component}}]]
        script = "swell task MoveDaRestart $config -d $datetime -m {{model_component}}"

    [[StageJedi-{{model_component}}]]
        script = "swell task StageJedi $config -m {{model_component}}"

    [[StageJediCycle-{{model_component}}]]
        script = "swell task StageJedi $config -d $datetime -m {{model_component}}"

    [[GetObservations-{{model_component}}]]
        script = "swell task GetObservations $config -d $datetime -m {{model_component}}"

    [[GenerateBClimatology-{{model_component}}]]
        script = "swell task GenerateBClimatology $config -d $datetime -m {{model_component}}"
        platform = {{platform}}
        execution time limit = {{scheduling["GenerateBClimatology"]["execution_time_limit"]}}
        [[[directives]]]
        {%- for key, value in scheduling["GenerateBClimatology"]["directives"][model_component].items() %}
            --{{key}} = {{value}}
        {%- endfor %}

    {% if 'cice6' in models["geos_marine"]["marine_models"] %}

    [[RunJediConvertStateSoca2ciceExecutable-{{model_component}}]]
        script = "swell task RunJediConvertStateSoca2ciceExecutable $config -d $datetime -m {{model_component}}"
        platform = {{platform}}
        execution time limit = {{scheduling["RunJediConvertStateSoca2ciceExecutable"]["execution_time_limit"]}}
        [[[directives]]]
        {%- for key, value in scheduling["RunJediConvertStateSoca2ciceExecutable"]["directives"][model_component].items() %}
            --{{key}} = {{value}}
        {%- endfor %}

    {% endif %}

    [[RenderJediObservations-{{model_component}}]]
        script = "swell task RenderJediObservations $config -d $datetime -m {{model_component}}"

    [[RunJediFgatExecutable-{{model_component}}]]
        script = "swell task RunJediFgatExecutable $config -d $datetime -m {{model_component}}"
        platform = {{platform}}
        execution time limit = {{scheduling["RunJediFgatExecutable"]["execution_time_limit"]}}
        execution retry delays = 1*PT10M
        [[[directives]]]
        {%- for key, value in scheduling["RunJediFgatExecutable"]["directives"][model_component].items() %}
            --{{key}} = {{value}}
        {%- endfor %}

    [[EvaJediLog-{{model_component}}]]
        script = "swell task EvaJediLog $config -d $datetime -m {{model_component}}"

    [[EvaIncrement-{{model_component}}]]
        script = "swell task EvaIncrement $config -d $datetime -m {{model_component}}"

    [[EvaObservations-{{model_component}}]]
        script = "swell task EvaObservations $config -d $datetime -m {{model_component}}"
        platform = {{platform}}
        execution time limit = {{scheduling["EvaObservations"]["execution_time_limit"]}}
        [[[directives]]]
        {%- for key, value in scheduling["EvaObservations"]["directives"][model_component].items() %}
            --{{key}} = {{value}}
        {%- endfor %}

    [[SaveRestart-{{model_component}}]]
        script = "swell task SaveRestart $config -d $datetime -m {{model_component}}"

    [[SaveObsDiags-{{model_component}}]]
        script = "swell task SaveObsDiags $config -d $datetime -m {{model_component}}"

    [[PrepareAnalysis-{{model_component}}]]
        script = "swell task PrepareAnalysis $config -d $datetime -m {{model_component}}"

    [[CleanCycle-{{model_component}}]]
        script = "swell task CleanCycle $config -d $datetime -m {{model_component}}"
    {% endfor %}
>>>>>>>> develop:src/swell/suites/3dfgat_marine_cycle/flow.cylc

# --------------------------------------------------------------------------------------------------
