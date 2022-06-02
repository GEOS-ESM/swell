# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import re
import string
import yaml

from swell.utilities.string_utils import replace_vars

# --------------------------------------------------------------------------------------------------


def resolve_definitions(dictionary):
    """
    At the highest level of the dictionary are definitions, such as swell_dir: /path/to/swell.
    Elsewhere in the dictionary is use of these definitions, such as key: $(swell_dir)/some/file.ext
    In this script variables like $(swell_dir) are replaced everywhere in the dictionary using the
    definition.

    Parameters
    ----------
    dictionary : dictionary, required
                 Dictionary to be modified

    Returns
    -------
    dictionary: dictionary
                Dictionary with any definitions resolved
    """

    # Convert dictionary to string representation in yaml form
    dictionary_string = yaml.dump(dictionary)

    # Get definitions in dictionary
    defs = {}
    defs.update({k: str(v) for k, v in iter(dictionary.items())
                if not isinstance(v, dict) and not isinstance(v, list)})

    # Replace the definitions everywhere in the dictionary
    dictionary_string = replace_vars(dictionary_string, **defs)

    # Convert back to dictionary
    dictionary = yaml.safe_load(dictionary_string)

    return dictionary


# --------------------------------------------------------------------------------------------------


def replace_vars_dict(d, **defs):
    """
    At the highest level of the dictionary are definitions, such as swell_dir: /path/to/swell.
    Elsewhere in the dictionary is use of these definitions, such as key: $(swell_dir)/some/file.ext
    In this script variables like $(swell_dir) are replaced everywhere in the dictionary using the
    definition.

    Parameters
    ----------
    d : dictionary, required
        Dictionary to be modified
    defs: dictionary, required
          Dictionary of definitions for resolving variables expressed as key-word arguments.

    Returns
    -------
    d_interp: dictionary
              Dictionary with any definitions resolved
    """

    # Convert dictionary to string representation in yaml form
    d_string = yaml.dump(d)

    # Replace the definitions everywhere in the dictionary
    d_string = replace_vars(d_string, **defs)

    # Convert back to dictionary
    d_interp = yaml.safe_load(d_string)

    return d_interp


# --------------------------------------------------------------------------------------------------


def dict_iterate_and_remove(d, key_to_remove, found):

    if isinstance(d, dict):

        for key, value in d.items():

            if key == key_to_remove:
                # To prevent changing the dictionary size within the loop we
                # have to return up to the level above. As such this routine
                # needs to be called repeatedly until the key to be removed
                # is no longer found. The found list provides a mutable entity
                # to track that the routine changes the dictionary in some way.
                del d[key]
                found.append(True)
                return

            if isinstance(value, dict):

                dict_iterate_and_remove(value, key_to_remove, found)

            elif isinstance(value, list):

                for value_item in value:

                    dict_iterate_and_remove(value_item, key_to_remove, found)


# --------------------------------------------------------------------------------------------------


def remove_matching_keys(d, key_to_remove, logger):
    """
    Removes all matching keys from a dictionary. Done by converting to string and going line by line
    If 'key:' is found in the line it will remove that line

    Parameters
    ----------
    d : dictionary, required
        Dictionary to be modified
    key: string, required
         Key to be removed where ever found in the file

    Returns
    -------
    d_new: dictionary
           Dictionary with matching keys removed
    """

    # List that will be appended by the search
    found = []

    # Max number of times to call the removal routine
    max_tries = 100
    for i in range(1, max_tries+1):
        found_len_prev = len(found)
        dict_iterate_and_remove(d, key_to_remove, found)
        if len(found) == found_len_prev:
            i = 0
            break

    # Issue abort if the maximum number of tries was reached.
    if i == max_tries:
        logger.abort('In remove_matching_keys the maximum tries to remove the key was reached.')

    return d


# --------------------------------------------------------------------------------------------------
