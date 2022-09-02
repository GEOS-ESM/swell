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

def get_element(logger, d, key, default = None):

    # Check that key exists
    if key not in d.keys():
        if default is None:
            logger.abort(f'Key {key} not found in the dictionary')
        else:
            element = default
    else:
        element = d[key]

    return element


# --------------------------------------------------------------------------------------------------
