# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import copy
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


def add_comments_to_dictionary(logger, dictionary_string_as_yaml, comment_dictionary):

    # Split the dictionary string lines into list
    dict_str_items = dictionary_string_as_yaml.split('\n')

    # Insertion elements
    insert_elements = []

    # Enumerate through the dictionary string items
    for ind, dict_str_item in enumerate(dict_str_items):

        # Skip empty lines
        if dict_str_item.strip() == '':
            continue

        # To make sure we are not on a list item skip if the first non-white space character is '-'
        if dict_str_item.strip()[0] == '-':
            continue

        # The first key is the string before the first colon
        key_in_comment_dict = dict_str_item.split(':')[0].strip()

        # Count number of spaces at the beginning of the line
        num_spaces = len(dict_str_item) - len(dict_str_item.lstrip())

        # Abort if the number of spaces is greater than two.
        if num_spaces > 2:
            logger.abort('The add_comments_to_dictionary function is not able to dictionaries ' +
                         'more than doubly nested.')

        # If there are two spaces at the beginning of the line, then the item is nested. Iterate
        # backwards through the list until the number of spaces at the beginning of the line is
        # reduced to zero. This will give the nesting of the item.
        if num_spaces == 2:

            found = False

            for ind2 in range(ind, -1, -1):

                if dict_str_item.strip()[0] == '-':
                    continue

                # Count number of spaces at the beginning of the line
                if len(dict_str_items[ind2]) - len(dict_str_items[ind2].lstrip()) == 0:
                    key_in_comment_dict = dict_str_items[ind2].split(':')[0].strip() + '.' + \
                        key_in_comment_dict
                    found = True
                    break

            if not found:
                logger.abort('The add_comments_to_dictionary function did not find the parent ' +
                             'of a nested dictionary item.')

        insert_elements.append((ind, "\n" + " "*num_spaces + "# " + comment_dictionary[key_in_comment_dict]))

    # Loop backwards through the insert elements and insert the comment
    for ind, comment in insert_elements[::-1]:
       dict_str_items.insert(ind, comment)

    # Strip new line marker from first item
    dict_str_items[0] = dict_str_items[0].split('\n')[1]

    # Return rejoined dictionary string
    return '\n'.join(dict_str_items)


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
