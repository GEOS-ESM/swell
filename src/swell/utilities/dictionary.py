# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import yaml
from collections.abc import Hashable


# --------------------------------------------------------------------------------------------------


def dict_get(logger, dictionary, key, default='NODEFAULT'):

    if key in dictionary.keys():

        return dictionary[key]

    else:

        if default == 'NODEFAULT':
            logger.abort(f'In dict_get the key \'{key}\' was not found in the dictionary and no ' +
                         f'default was provided.')
        else:
            return default


# --------------------------------------------------------------------------------------------------


def remove_matching_keys(d, key):
    """
    Recursively locates and removes all dictionary items matching the supplied key.
    Parameters
    ----------
    d : root node, required
        traversable data structure (dictionary or list) to be searched.
    key: string, required
         Key to be removed
    """

    if isinstance(d, dict):

        d.pop(key, None)

        for k, v in iter(d.items()):
            if not isinstance(v, Hashable):
                remove_matching_keys(v, key)

    elif isinstance(d, list):

        for v in d:
            if not isinstance(v, Hashable):
                remove_matching_keys(v, key)


# --------------------------------------------------------------------------------------------------

def add_comments_to_dictionary(logger, dictionary_string, comment_dictionary):

    dict_str_items = dictionary_string.split('\n')

    for key in comment_dictionary.keys():

        keys_hierarchy = key.split('.')
        indent_ind = len(key.split('.')) - 1
        indent = indent_ind*2*' '

        if indent_ind == 0:

            for ind, dict_str_item in enumerate(dict_str_items):

                if dict_str_item[0:len(key)+1] == key + ':':

                    dict_str_items.insert(max(0, ind), '\n# ' + comment_dictionary[key])
                    break

        else:

            index_of_key = 0
            for key_hierarchy in keys_hierarchy:

                for line in range(index_of_key, len(dict_str_items)):

                    if ' ' + key_hierarchy + ':' in dict_str_items[line]:

                        index_of_key = line

                        break

            dict_str_items.insert(max(0, index_of_key), '\n' + indent + '# ' +
                                  comment_dictionary[key])

    # Remove empty line at the beginning
    if dict_str_items[0][0] == '\n':
        dict_str_items[0] = dict_str_items[0][1:]

    dictionary_string_with_comments = '\n'.join(dict_str_items)

    return dictionary_string_with_comments


# --------------------------------------------------------------------------------------------------


def replace_string_in_dictionary(dictionary, string_in, string_out):

    # Convert dictionary to string
    dictionary_string = yaml.dump(dictionary, default_flow_style=False, sort_keys=False)

    # Replace string in the dictionary
    dictionary_string = dictionary_string.replace(string_in, string_out)

    # Convert back to dictionary
    return yaml.safe_load(dictionary_string)


# --------------------------------------------------------------------------------------------------


def write_dict_to_yaml(dictionary, file):

    # Convert dictionary to YAML string
    dictionary_string = yaml.dump(dictionary, default_flow_style=False, sort_keys=False)

    # Write string to file
    with open(file, 'w') as file_open:
        file_open.write(dictionary_string)


# --------------------------------------------------------------------------------------------------


def update_dict(orig_dict, overwrite_dict):

    # Create output dictionary from original dictionary
    output_dict = orig_dict.copy()

    for key, value in overwrite_dict.items():
        if isinstance(value, dict) and key in output_dict and isinstance(output_dict[key], dict):
            output_dict[key] = update_dict(output_dict[key], value)
        else:
            output_dict[key] = value

    return output_dict


# --------------------------------------------------------------------------------------------------


def dictionary_override(logger, orig_dict, override_dict):
    for key, value in override_dict.items():
        if value == 'REMOVE':
            orig_dict.pop(key, None)
        elif isinstance(value, dict) and key in orig_dict and isinstance(orig_dict[key], dict):
            dictionary_override(logger, orig_dict[key], value)
        else:
            orig_dict[key] = value

    return orig_dict


# --------------------------------------------------------------------------------------------------
