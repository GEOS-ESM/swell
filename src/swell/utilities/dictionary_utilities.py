# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import re
import string
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


def add_comments_to_dictionary(dictionary_string, comment_dictionary):

    dict_str_items = dictionary_string.split('\n')

    for key in comment_dictionary.keys():

        keys_hierarchy = key.split('.')
        indent_ind = len(key.split('.')) - 1
        indent = indent_ind*2*' '

        if indent_ind == 0:

            for ind, dict_str_item in enumerate(dict_str_items):

                if key + ':' in dict_str_item:

                    dict_str_items.insert(max(0, ind), '\n# ' + comment_dictionary[key])
                    break

        else:

            index_of_key = 0
            for key_hierarchy in keys_hierarchy:

                for line in range(index_of_key, len(dict_str_items)):

                    if key_hierarchy + ':' in dict_str_items[line]:

                        index_of_key = line

                        break

            dict_str_items.insert(max(0, index_of_key), '\n' + indent + '# ' +
                                  comment_dictionary[key])

    dictionary_string_with_comments = '\n'.join(dict_str_items)

    return dictionary_string_with_comments


# --------------------------------------------------------------------------------------------------
