# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


def camel_case_to_snake_case(CamelCaseString: str) -> str:

    # Convert a string that looks like e.g. ThisIsAString to this_is_a_string
    # -----------------------------------------------------------------------
    snake_case_string = ""
    for char in CamelCaseString:
        if char.isupper():
            snake_case_string += "_" + char.lower()
        else:
            snake_case_string += char
    return snake_case_string.lstrip("_")


# --------------------------------------------------------------------------------------------------


def snake_case_to_camel_case(snake_case_string: str) -> str:

    # Convert a string that looks like e.g. this_is_a_string to ThisIsAString
    # -----------------------------------------------------------------------
    words = snake_case_string.split('_')
    CamelCaseString = words[0].capitalize() + ''.join(word.capitalize() for word in words[1:])
    return CamelCaseString


# --------------------------------------------------------------------------------------------------
