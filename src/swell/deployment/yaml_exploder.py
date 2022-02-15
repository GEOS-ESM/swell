# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.utilities.string_utils import replace_vars


# --------------------------------------------------------------------------------------------------


def recursive_yaml_expansion(experiment_dict):
    '''
    Expands the experiment yaml file into a readable expanded yaml file that the workflow engine
    will use
    '''
    # Loop over experiment yaml and expand
    for k in experiment_dict.keys():

        # Get the dictionary element
        param_list = experiment_dict[k]

        # Checks for yaml file type, and if there is a list of files or single file. List type
        # requires an additional loop to tease out individual files. Alternative would be to
        # check if something is a string, if yes, then force into list. However, that may cause
        # problems later

        if 'yaml::' in str(param_list) and isinstance(param_list, list):
            exp_list = []
            for p in param_list:
                # Call the pull_yaml function
                big_yaml = pull_yaml(experiment_dict, p)
                # Append the dictionary to the expanded list
                exp_list.append(big_yaml)
            # Write the expanded list element to the original dictionary key
            experiment_dict[k] = exp_list
        elif 'yaml::' in str(param_list):
            # Call the pull_yaml function
            big_yaml = pull_yaml(experiment_dict, param_list)
            # Assign the expanded yaml to the original ditionary key
            experiment_dict[k] = big_yaml


# --------------------------------------------------------------------------------------------------


def pull_yaml(experiment_dict,  param):
    '''
    Takes a yaml line in the experiment file and replaces it with the opened yaml file.
    '''
    # Set useful directory path variables
    stage_dir = experiment_dict['stage_dir']
    bundle_dir = experiment_dict['bundle_dir']
    run_dir = os.path.join(experiment_dict['experiment_dir'], '{{current_cycle}}')

    # Extract path to yaml file and replace variables
    yaml_file_name = param.split('yaml::')[1]
    yaml_file_name = yaml_file_name.replace('$(bundle_dir)', bundle_dir)

    # Open the new yaml as text
    with open(yaml_file_name, 'r') as yaml_file:
        sub_yaml_text = yaml_file.read()

    # Replace the directories and experiment ID variables specific to this run
    sub_yaml_text = replace_vars(sub_yaml_text, stage_dir=stage_dir,
                                 experiment_id_dir=experiment_dict['experiment_dir'],
                                 run_dir=run_dir, experiment=experiment_dict['experiment_id'])
    sub_yaml_dict = yaml.safe_load(sub_yaml_text)

    return sub_yaml_dict


# --------------------------------------------------------------------------------------------------
