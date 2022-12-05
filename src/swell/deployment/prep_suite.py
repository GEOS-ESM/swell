# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from swell.utilities.dictionary import dict_get
from swell.utilities.jinja2 import template_string_jinja2


# --------------------------------------------------------------------------------------------------


def prepare_cylc_suite_jinja2(logger, swell_suite_path, exp_suite_path, experiment_dict):

    # Open suite file from swell
    # --------------------------
    with open(os.path.join(swell_suite_path, 'flow.cylc'), 'r') as file:
        suite_file = file.read()

    # Copy the experiment dictionary to the rendering dictionary
    # ----------------------------------------------------------
    render_dictionary = experiment_dict

    # Get unique list of cycle times with model flags to render dictionary
    # --------------------------------------------------------------------
    model_components = dict_get(logger, experiment_dict, 'model_components', [])
    cycle_times = []
    for model_component in model_components:
        cycle_times = list(set(cycle_times + experiment_dict['models'][model_component]['cycle_times']))
    cycle_times.sort()

    cycle_times_dict_list = []
    for cycle_time in cycle_times:
        cycle_time_dict = {}
        cycle_time_dict['cycle_time'] = cycle_time
        for model_component in model_components:
            cycle_time_dict[model_component] = False
            if cycle_time in experiment_dict['models'][model_component]['cycle_times']:
                cycle_time_dict[model_component] = True
        cycle_times_dict_list.append(cycle_time_dict)

    render_dictionary['cycle_times'] = cycle_times_dict_list

    # Add scheduling to the render dictionary (TODO: do not hard code this)
    # ---------------------------------------
    render_dictionary['scheduling'] = {}
    render_dictionary['scheduling']['RunJediHofxExecutable'] = {}
    render_dictionary['scheduling']['RunJediHofxExecutable']['execution_time_limit'] = 'PT2H'
    render_dictionary['scheduling']['RunJediHofxExecutable']['account'] = 'g0613'
    render_dictionary['scheduling']['RunJediHofxExecutable']['qos'] = 'allnccs'
    render_dictionary['scheduling']['RunJediHofxExecutable']['constraint'] = 'hasw'
    render_dictionary['scheduling']['RunJediHofxExecutable']['nodes'] = 1
    render_dictionary['scheduling']['RunJediHofxExecutable']['ntasks_per_node'] = 24

    render_dictionary['scheduling']['BuildJedi'] = {}
    render_dictionary['scheduling']['BuildJedi']['execution_time_limit'] = 'PT4H'
    render_dictionary['scheduling']['BuildJedi']['account'] = 'g0613'
    render_dictionary['scheduling']['BuildJedi']['qos'] = 'allnccs'
    render_dictionary['scheduling']['BuildJedi']['constraint'] = 'hasw'
    render_dictionary['scheduling']['BuildJedi']['nodes'] = 1
    render_dictionary['scheduling']['BuildJedi']['ntasks_per_node'] = 24

    # Render the template
    # -------------------
    new_suite_file = template_string_jinja2(logger, suite_file, render_dictionary)

    # Write suite file to experiment
    # ------------------------------
    with open(os.path.join(exp_suite_path, 'flow.cylc'), 'w') as file:
        file.write(new_suite_file)


# --------------------------------------------------------------------------------------------------
