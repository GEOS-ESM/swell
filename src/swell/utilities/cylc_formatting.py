# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from typing import Union, Optional, Self
from collections.abc import Mapping

# --------------------------------------------------------------------------------------------------

indent = '    '


def format_dict(dictionary: Mapping):
    # Convert a dictionary into a string

    dict_str = ''

    for key, value in dictionary.items():
        dict_str += f'{key} = {value}\n'

    return dict_str

# --------------------------------------------------------------------------------------------------


def indent_lines(string: str, level: int = 0, reset: bool = False):
    # Reset line indentation for string, and indent lines by level

    out_string = ''

    for line in string.split('\n'):
        if reset:
            line = line.strip()

        if len(line) > 0:
            line = f'{indent*level}{line}'

        out_string += f'{line}\n'

    return out_string

# --------------------------------------------------------------------------------------------------


def format_section(section: Self, level: int = 0) -> str:
    # Format a string to match cylc's section syntax
    # format the header with the appropriate amount of enclosing brackets and indents

    section_str = ''

    name = section.name
    if name is not None:
        section_str += f'{indent*level}{(level+1)*"["}{name}{"]"*(level+1)}\n'
    else:
        level -= 1

    content = section.content
    if isinstance(content, Mapping):
        content = format_dict(content)

    section_str += indent_lines(content, level+1)

    return section_str

# --------------------------------------------------------------------------------------------------


class CylcSection():
    '''
    Holds the information contained in a section, including the name and contents, which can be a
    string or dictionary. Also tracks child subsections, automatically handling indentation
    and syntax at the time when the string is retrieved.
    '''

    def __init__(self, name: Optional[str] = None, content: Union[str, dict] = '') -> None:
        self.name = name
        self.content = content

        self.subsections = []

    def __format_section__(self, section: Self, level: int = 0) -> str:
        section_str = ''

        name = section.name
        if name is not None:
            section_str += f'{indent*level}{(level+1)*"["}{name}{"]"*(level+1)}\n'
        else:
            level -= 1

        content = section.content
        if isinstance(content, Mapping):
            content = format_dict(content)

        section_str += indent_lines(content, level+1, False)

        if level == 0:
            section_str += f'# {"-"*98}\n\n'

        return section_str

    def add_subsection(self, subsection: Self) -> None:
        self.subsections.append(subsection)

    def get_section_str(self, level: int = 0) -> str:
        section_str = format_section(self, level)

        for subsection in self.subsections:
            section_str += subsection.get_section_str(level+1)

        if level == 0:
            section_str += f'# {"-"*98}\n\n'

        return section_str


# --------------------------------------------------------------------------------------------------
