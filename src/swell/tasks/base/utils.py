# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


def camelcase_to_underscore(CamelCaseString):

    # Convert a string that looks like e.g. ThisIsAString to this_is_a_string
    # -----------------------------------------------------------------------

    # Create empty output string
    underscore_string = ''

    # Loop over the elements in the string
    for element in CamelCaseString:

        # Check if element is upper case and if so prepend with underscore
        if element.isupper():
            new_element = '_'+element.lower()
        else:
            new_element = element

        # Add new element to the output string
        underscore_string = underscore_string+new_element

    # If this results in leading underscore then remove it
    if underscore_string[0] == "_":
        underscore_string = underscore_string[1:]

    return underscore_string


# --------------------------------------------------------------------------------------------------
