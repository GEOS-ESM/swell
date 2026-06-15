# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.jinja2 import template_string_jinja2
from swell.suites.base.cylc_workflow import CylcWorkflow
from swell.tasks.base.task_attributes import task_attributes as ta
from swell.tasks.base.task_setup import TaskSetup
from swell.suites.base.suite_attributes import workflows

# --------------------------------------------------------------------------------------------------

template_str = '''
# --------------------------------------------------------------------------------------------------

# Cylc suite for executing JEDI-based non-cycling variational data assimilation

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
            # Clone JEDI source code
            CloneJedi

            # Build JEDI source code by linking
            CloneJedi => BuildJediByLinking?

            # If not able to link to build create the build
            BuildJediByLinking:fail? => BuildJedi
        """

        {% for cycle_time in cycle_times %}
        {{cycle_time.cycle_time}} = """
        {% for model_component in model_components %}
        {% if cycle_time[model_component] %}
            # Task triggers for: {{model_component}}
            # ------------------
            # Ensure previous cycle completes before starting this one
            CleanCycle-{{model_component}}[-{{models[model_component]["window_length"]}}] => GetBackground-{{model_component}}

            # Generate background error covariance
            GetBackground-{{model_component}} => RunJediVariationalExecutable-{{model_component}}

            # Perform staging that is cycle dependent
            StageJediCycle-{{model_component}}

            # Run Jedi variational executable
            BuildJediByLinking[^]? | BuildJedi[^]  => RunJediVariationalExecutable-{{model_component}}
            StageJediCycle-{{model_component}} => RunJediVariationalExecutable-{{model_component}}
            GetBackground-{{model_component}} => RunJediVariationalExecutable-{{model_component}}

            GetObservations-{{model_component}} => RenderJediObservations-{{model_component}}
            RenderJediObservations-{{model_component}} => RunJediVariationalExecutable-{{model_component}}

            # Prepare forecast task, Update RC files, and create scratch directory
            RunJediVariationalExecutable-{{model_component}} => PrepForecastCf-{{model_component}}

            # Get restart files from R2D2
            PrepForecastCf-{{model_component}} => GetRestartCf-{{model_component}}

            # Run forecast
            GetRestartCf-{{model_component}} => RunForecast-{{model_component}}

            # Save forecast
            RunForecast-{{model_component}} => SaveForecastCf-{{model_component}}

            # Save restart files to R2D2
            RunForecast-{{model_component}} => SaveRestartCf-{{model_component}}

            # EvaObservations
            RunJediVariationalExecutable-{{model_component}} => EvaObservations-{{model_component}}

            # EvaJediLog
            RunJediVariationalExecutable-{{model_component}} => EvaJediLog-{{model_component}}

            # EvaIncrement
            RunJediVariationalExecutable-{{model_component}} => EvaIncrement-{{model_component}}

            # Save observations
            RunJediVariationalExecutable-{{model_component}} => SaveObsDiags-{{model_component}}

            # Clean up large files
            EvaObservations-{{model_component}} & EvaJediLog-{{model_component}} & EvaIncrement-{{model_component}} &
            SaveObsDiags-{{model_component}} & SaveForecastCf-{{model_component}} & SaveRestartCf-{{model_component}} => CleanCycle-{{model_component}}

        {% endif %}
        {% endfor %}
        """
        {% endfor %}

# --------------------------------------------------------------------------------------------------

[runtime]

    # Task defaults
    # -------------

'''  # noqa

# --------------------------------------------------------------------------------------------------


class RunForecast(TaskSetup):
    def set_defaults(self):
        self.base_name = 'RunForecast'
        self.script = """cycle_dir=$(python3 -c 'from swell.utilities.datetime_util import Datetime; import sys; print(Datetime(sys.argv[1]).string_directory())' "$CYLC_TASK_CYCLE_POINT")
            scratch_dir="{{experiment_root}}/{{experiment_id}}/run/${cycle_dir}/{{model_component}}/scratch"
            forecast_log="${scratch_dir}/CFv2_gcm_${SLURM_JOB_ID:-$$}"
            "${scratch_dir}/gcm_run_geoscf.j" > "${forecast_log}" 2>&1
            """  # noqa
        self.is_cycling = True
        self.model_dep = True
        self.slurm = {'ntasks-per-node': 108, 'nodes': 8, 'job-name': 'CFv2rc1t13',
                      'output': '/dev/null', 'time': '00:40:00'}


@workflows.register('3dvar_cf_cycle')
class Workflow_3dvar_cf_cycle(CylcWorkflow):

    def get_workflow_string(self):
        workflow_str = self.default_header()

        self.experiment_dict['stall_timeout'] = """\
        {% if environ.get('SWELL_CYLC_TIMEOUT') %}
        [[events]]
        stall timeout = {{environ['SWELL_CYLC_TIMEOUT']}}
        {% endif %}"""

        workflow_str += template_string_jinja2(logger=self.logger,
                                               templated_string=template_str,
                                               dictionary_of_templates=self.experiment_dict,
                                               allow_unresolved=True)

        for task in self.tasks:
            workflow_str += task.runtime_string(self.experiment_dict,
                                                self.slurm_external)

        workflow_str = template_string_jinja2(self.logger, workflow_str, self.experiment_dict, True)

        return workflow_str

    def set_tasks(self) -> list:

        self.tasks.append(ta.root())
        self.tasks.append(ta.CloneJedi())
        self.tasks.append(ta.BuildJediByLinking())
        self.tasks.append(ta.BuildJedi())

        for model in self.experiment_dict['model_components']:
            self.tasks.append(ta.StageJediCycle(model=model))
            self.tasks.append(ta.GetBackground(model=model))
            self.tasks.append(ta.GetObservations(model=model))
            self.tasks.append(ta.RenderJediObservations(model=model))
            self.tasks.append(ta.RunJediVariationalExecutable(model=model))
            self.tasks.append(ta.GetRestartCf(model=model))
            self.tasks.append(ta.PrepForecastCf(model=model))
            self.tasks.append(RunForecast(model=model))
            self.tasks.append(ta.EvaIncrement(model=model))
            self.tasks.append(ta.SaveRestartCf(model=model))
            self.tasks.append(ta.SaveForecastCf(model=model))
            self.tasks.append(ta.EvaJediLog(model=model))
            self.tasks.append(ta.EvaObservations(model=model))
            self.tasks.append(ta.SaveObsDiags(model=model))
            self.tasks.append(ta.CleanCycle(model=model))

# --------------------------------------------------------------------------------------------------
