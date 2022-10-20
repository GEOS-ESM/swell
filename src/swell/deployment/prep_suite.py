# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import importlib
import jinja2
import os
import yaml


# --------------------------------------------------------------------------------------------------


def prepare_cylc_suite_jinja2(logger, exp_suite_path, experiment_dict):

    # Open suite file
    # ---------------
    with open(os.path.join(exp_suite_path, 'flow.cylc'), 'r') as file:
        suite_file = file.read()

    # Copy the experiment dictionary to the rendering dictionary
    # ----------------------------
    render_dictionary = experiment_dict

    # Get unique list of cycle times with model flags to render dictionary
    # --------------------------------------------------------------------
    cycle_times = []
    for model in experiment_dict['model_components']:
        cycle_times = list(set(cycle_times + experiment_dict['models'][model]['cycle_times']))
    cycle_times.sort()

    cycle_times_dict_list = []
    for cycle_time in cycle_times:
        cycle_time_dict = {}
        cycle_time_dict['cycle_time'] = cycle_time
        for model in experiment_dict['model_components']:
            cycle_time_dict[model] = False
            if cycle_time in experiment_dict['models'][model]['cycle_times']:
                cycle_time_dict[model] = True
        cycle_times_dict_list.append(cycle_time_dict)

    render_dictionary['cycle_times'] = cycle_times_dict_list

    print(yaml.dump(render_dictionary, default_flow_style=False, sort_keys=False))

    # Add scheduling to the render dictionary
    # ---------------------------------------
    render_dictionary['scheduling'] = {}
    render_dictionary['scheduling']['RunJediExecutable'] = {}
    render_dictionary['scheduling']['RunJediExecutable']['execution_time_limit'] = 'PT1H'
    render_dictionary['scheduling']['RunJediExecutable']['account'] = 'g0613'
    render_dictionary['scheduling']['RunJediExecutable']['qos'] = 'debug'
    render_dictionary['scheduling']['RunJediExecutable']['constraint'] = 'debug'
    render_dictionary['scheduling']['RunJediExecutable']['nodes'] = 1
    render_dictionary['scheduling']['RunJediExecutable']['ntasks_per_node'] = 28

    #print(render_dictionary['cycle_times'])

    environment = jinja2.Environment()
    template = environment.from_string(suite_file)
    new_suite_file = template.render(render_dictionary)

    print(new_suite_file)

    return










    # Configuration things
    # --------------------
    suite_dir = experiment_dict['suite_dir']

    suite_dict = experiment_dict['suite']

    # Setup the platform specific
    if 'platform' in suite_dict and 'scheduling' in suite_dict:
        platform = suite_dict['platform']
        scheduling_dicts = suite_dict['scheduling']

        # Loop and get default scheduling dictionary
        # ------------------------------------------
        for scheduling_dict in scheduling_dicts:
            if scheduling_dict['task'] == 'Default':
                def_scheduling_dict = scheduling_dict

        # Get default tasks per node depending on platform/constraint
        plat_mod = importlib.import_module('swell.deployment.platforms.'+platform+'.scheduling')
        get_tasks_per_node_call = getattr(plat_mod, 'get_tasks_per_node')
        dtpn = get_tasks_per_node_call(platform, def_scheduling_dict['constraint'])
        def_scheduling_dict['ntasks_per_node'] = dtpn

        # Loop and set task dictionaries
        # ------------------------------
        for scheduling_dict in scheduling_dicts:

            if scheduling_dict['task'] != 'Default':
                # Merge the default and task specific values
                task_merged = ({**def_scheduling_dict, **scheduling_dict})
                suite_dict[task_merged['task']] = task_merged

        del suite_dict['scheduling']

    # Convert dictionary to jinja2 like string
    suite_dict_jinja2_str = '{% set suite_properties = '+str(suite_dict)+'%}'

    # Write jinja2 dictionary to file in suite directory
    with open(os.path.join(suite_dir, 'suite.jinja2'), 'w') as suite_jinja2:
        suite_jinja2.write(suite_dict_jinja2_str)


# --------------------------------------------------------------------------------------------------
