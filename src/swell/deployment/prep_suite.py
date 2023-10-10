# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import yaml

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
    render_dictionary = {}

    # Elements to copy from the experiment dictionary
    # -----------------------------------------------
    render_elements = [
        'start_cycle_point',
        'final_cycle_point',
        'runahead_limit',
        'model_components',
        'platform',
    ]

    # Copy elements from experiment dictionary to render dictionary
    # -------------------------------------------------------------
    for element in render_elements:
        if element in experiment_dict:
            render_dictionary[element] = experiment_dict[element]

    # Get unique list of cycle times with model flags to render dictionary
    # --------------------------------------------------------------------

    # Check if 'cycle_times' appears anywhere in the suite_file
    if 'cycle_times' in suite_file:

        # Since cycle times are used, the render_dictionary will need to include cycle_times
        model_components = dict_get(logger, experiment_dict, 'model_components', [])

        # If there are different model components then process each to gather cycle times
        if len(model_components) > 0:
            cycle_times = []
            for model_component in model_components:
                cycle_times_mc = experiment_dict['models'][model_component]['cycle_times']
                cycle_times = list(set(cycle_times + cycle_times_mc))
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

        # Otherwise check that experiment_dict has cycle_times
        elif 'cycle_times' in experiment_dict:

            cycle_times = list(set(experiment_dict['cycle_times']))
            cycle_times.sort()
            render_dictionary['cycle_times'] = cycle_times

        else:

            # Otherwise use logger to abort
            logger.abort('The suite file required cycle_times but there are no model components ' +
                         'to gather them from or they are not provided in the experiment ' +
                         'dictionary.')

    # Look for a file called $HOME/.swell/slurm.yaml
    # ----------------------------------------------
    yaml_path = os.path.expanduser("~/.swell/swell-slurm.yaml")
    slurm_global = {}
    if os.path.exists(yaml_path):
        logger.info(f'Found file containing swell slurm global values')
        with open(yaml_path, "r") as yaml_file:
            slurm_global = yaml.safe_load(yaml_file)

    # Set default values for global slurm values
    account = 'g0613'
    qos = 'allnccs'
    partition = None
    constraint = 'cas|sky'

    # Extract from slurm global file
    if 'qos' in slurm_global:
        qos = slurm_global['qos']

    if 'partition' in slurm_global:
        partition = slurm_global['partition']

    if 'account' in slurm_global:
        account = slurm_global['account']

    if 'constraint' in slurm_global:
        constraint = slurm_global['constraint']

    # List of tasks using slurm
    # -------------------------
    slurm_tasks = [
        'BuildJedi',
        'BuildGeos',
        'EvaObservations',
        'GenerateBClimatology',
        'RunJediHofxExecutable',
        'RunJediLetkfExecutable',
        'RunJediVariationalExecutable',
        'RunJediLetkfExecutable',
        'RunJediUfoTestsExecutable',
        'RunGeosExecutable',
        ]

    # Fill default values for slurm tasks
    # -----------------------------------
    render_dictionary['scheduling'] = {}
    for slurm_task in slurm_tasks:
        render_dictionary['scheduling'][slurm_task] = {}
        render_dictionary['scheduling'][slurm_task]['execution_time_limit'] = 'PT1H'
        render_dictionary['scheduling'][slurm_task]['account'] = account
        render_dictionary['scheduling'][slurm_task]['qos'] = qos
        render_dictionary['scheduling'][slurm_task]['nodes'] = 1
        render_dictionary['scheduling'][slurm_task]['ntasks_per_node'] = 40
        render_dictionary['scheduling'][slurm_task]['constraint'] = constraint
        render_dictionary['scheduling'][slurm_task]['partition'] = partition

    # Set some specific values for:
    # -----------------------------

    # run time
    render_dictionary['scheduling']['BuildJedi']['execution_time_limit'] = 'PT3H'
    render_dictionary['scheduling']['EvaObservations']['execution_time_limit'] = 'PT30M'

    # Render the template
    # -------------------
    new_suite_file = template_string_jinja2(logger, suite_file, render_dictionary)

    # Write suite file to experiment
    # ------------------------------
    with open(os.path.join(exp_suite_path, 'flow.cylc'), 'w') as file:
        file.write(new_suite_file)


# --------------------------------------------------------------------------------------------------
