# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import yaml

from swell.utilities.jinja2 import template_string_jinja2
from swell.suites.base.cylc_workflow import CylcWorkflow
from swell.tasks.base.task_attributes import task_attributes as ta
from swell.suites.base.suite_attributes import workflows

# --------------------------------------------------------------------------------------------------

template_str = '''
# --------------------------------------------------------------------------------------------------

# Cylc suite for running comparison tests on completed experiments

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
        {% for cycle_time in cycle_times %}
        {{cycle_time.cycle_time}} = """
        {% for model_component in model_components %}
        {% if cycle_time[model_component] %}
            {% for path in comparison_experiment_paths %}
            JediOopsLogParser-{{model_component}}-{{ loop.index0 }}
            {% endfor %}
            JediLogComparison-{{model_component}}?
            JediLogComparison-{{model_component}}:fail? => EvaComparisonIncrement-{{model_component}}
            JediLogComparison-{{model_component}}:fail? => EvaComparisonJediLog-{{model_component}}
            JediLogComparison-{{model_component}}:fail? => EvaComparisonObservations-{{model_component}} => comparison_fail
        {% endif %}
        {% endfor %}
        """
        {% endfor %}

# --------------------------------------------------------------------------------------------------

[runtime]

    # Task defaults
    # -------------

    [[comparison_fail]]
        script = "exit 1"

'''  # noqa

# --------------------------------------------------------------------------------------------------


@workflows.register('compare')
class Workflow_compare(CylcWorkflow):

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

    def set_tasks(self) -> list:

        paths = self.experiment_dict['comparison_experiment_paths']

        for path in paths:
            with open(path, 'r') as f:
                config_dict = yaml.safe_load(f)
            for model in self.experiment_dict['model_components']:
                num_of_iterations = config_dict['models'][model]['number_of_iterations']

                self.experiment_dict['models'][model]['number_of_iterations'] = num_of_iterations

        self.tasks.append(ta.root())

        for model in self.experiment_dict['model_components']:
            self.tasks.append(ta.EvaComparisonObservations(model=model))
            self.tasks.append(ta.EvaComparisonIncrement(model=model))
            self.tasks.append(ta.EvaComparisonJediLog(model=model))
            self.tasks.append(ta.JediLogComparison(model=model))

            for i, path in enumerate(paths):
                log_parser = ta.JediOopsLogParser(model=model)
                log_parser.scheduling_name = f'JediOopsLogParser-{model}-{i}'
                log_parser.script = (f'swell task JediOopsLogParser {paths[i]}'
                                     f' -d $datetime -m {model}')
                self.tasks.append(log_parser)

# --------------------------------------------------------------------------------------------------
