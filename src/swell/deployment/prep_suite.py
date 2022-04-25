# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import importlib
import os


# --------------------------------------------------------------------------------------------------


def prepare_suite(logger, experiment_dict):

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
