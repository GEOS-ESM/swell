# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import yaml


# --------------------------------------------------------------------------------------------------


def recursive_yaml_expansion(experiment_dict):
    '''
    Replace paths to yaml with the dictionary defined in that yaml
    '''
    # Loop over experiment yaml and expand
    for k in experiment_dict.keys():

        # Get the dictionary element (might be a list)
        experiment_item = experiment_dict[k]

        # Create list of items
        params = []
        if isinstance(experiment_item, list):
            params = params + experiment_item
        else:
            params.append(experiment_item)

        # Check if the item list contains the key string 'yaml::'
        if 'yaml::' in str(params):

            # Create empty list of dictionaries to be filled
            exp_list = []

            for param in params:

                # Read yaml into dictionary and append
                with open(param.split('yaml::')[1], 'r') as yaml_file:
                    sub_yaml_dict = yaml.safe_load(yaml_file)

                # Append the dictionary to the expanded list
                exp_list.append(sub_yaml_dict)

            # Write the expanded list element to the original dictionary key
            if len(exp_list) > 1:
                experiment_dict[k] = exp_list
            else:
                experiment_dict[k] = exp_list[0]


# --------------------------------------------------------------------------------------------------
