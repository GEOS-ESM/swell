# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


def camel_case_to_snake_case(CamelCaseString):

    # Convert a string that looks like e.g. ThisIsAString to this_is_a_string
    # -----------------------------------------------------------------------

    # Create empty output string
    snake_case_string = ''

    # Loop over the elements in the string
    for element in CamelCaseString:

        # Check if element is upper case and if so prepend with underscore
        if element.isupper():
            new_element = '_'+element.lower()
        else:
            new_element = element

        # Add new element to the output string
        snake_case_string = snake_case_string+new_element

    # If this results in leading underscore then remove it
    if snake_case_string[0] == "_":
        snake_case_string = snake_case_string[1:]

    return snake_case_string


# --------------------------------------------------------------------------------------------------
