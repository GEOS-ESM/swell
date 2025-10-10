# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.cylc_workflow import CylcWorkflow
from swell.utilities.check_da_params import check_da_params

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
            EvaComparisonIncrement-{{model_component}}
            EvaComparisonJediLog-{{model_component}}
            {% for path in comparison_experiment_paths %}
            JediOopsLogParser-{{model_component}}-{{ loop.index0 }} => JediLogComparison-{{model_component}}
            {% endfor %}
        {% endif %}
        {% endfor %}
        """
        {% endfor %}

# --------------------------------------------------------------------------------------------------
'''  # noqa

# --------------------------------------------------------------------------------------------------


class Workflow_compare_variational(CylcWorkflow):

    def define_initial_workflow(self):
        workflow_str = self.default_header()

        # Overrides for comparison suites
        start_cycle_point = self.experiment_dict['start_cycle_point']
        final_cycle_point = self.experiment_dict['final_cycle_point']
        if self.experiment_dict['start_cycle_point'] is None:
            config_list = self.experiment_dict['comparison_experiment_paths']
            for model in self.experiment_dict['model_components']:
                cycle_times = self.experiment_dict['models'][model]['cycle_times']
                start_cycle_point, final_cycle_point, cycle_times = check_da_params(
                        config_list,
                        model,
                        start_cycle_point,
                        final_cycle_point,
                        cycle_times)

                self.experiment_dict['start_cycle_point'] = start_cycle_point
                self.experiment_dict['final_cycle_point'] = final_cycle_point
                self.experiment_dict['models'][model]['cycle_times'] = cycle_times

        workflow_str += template_string_jinja2(logger=self.logger,
                                               templated_string=template_str,
                                               dictionary_of_templates=self.experiment_dict,
                                               allow_unresolved=True)

        return workflow_str

# --------------------------------------------------------------------------------------------------
