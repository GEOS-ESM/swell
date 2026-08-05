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

[scheduler]
    UTC mode = True
    allow implicit tasks = False

{{stall_timeout}}

[scheduling]
    initial cycle point = {{start_cycle_point}}
    final cycle point = {{final_cycle_point}}

    [[graph]]

        {% if download_convert_pipeline %}
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
        {% endif %}

        {% for cycle_time in cycle_times %}
            {{cycle_time.cycle_time}} = """
                {% for model_component in model_components %}
                {% if download_convert_pipeline %}
                DownloadObs-{{model_component}} => ConvertObsToIoda-{{model_component}}
                BuildJediByLinking[^]? | BuildJedi[^]  => ConvertObsToIoda-{{model_component}}
                ConvertObsToIoda-{{model_component}} => IngestObs-{{model_component}}
                {% elif ingest_background_pipeline %}
                SaveBackground-{{model_component}}
                {% else %}
                IngestObs-{{model_component}}
                {% endif %}
                {% endfor %}
            """
        {% endfor %}

# --------------------------------------------------------------------------------------------------

[runtime]

'''  # noqa

# --------------------------------------------------------------------------------------------------


@workflows.register('r2d2_ingest')
class Workflow_r2d2_ingest(CylcWorkflow):

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

        return workflow_str

    def set_tasks(self) -> list:

        self.tasks.append(ta.root())
        self.tasks.append(ta.CloneJedi())
        self.tasks.append(ta.BuildJediByLinking())
        self.tasks.append(ta.BuildJedi())
        for model in self.experiment_dict['model_components']:
            self.tasks.append(ta.DownloadObs(model=model))
            self.tasks.append(ta.ConvertObsToIoda(model=model))
            self.tasks.append(ta.IngestObs(model=model))
            self.tasks.append(ta.SaveBackground(model=model))

# --------------------------------------------------------------------------------------------------
