# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from typing import Union, Optional, Self
from collections.abc import Mapping
import textwrap

INDENT = ' ' * 4

# --------------------------------------------------------------------------------------------------


def format_dict(dictionary: Mapping):
    """Convert a dictionary into a string.

    Args:
        dictionary (Mapping): The dictionary to format.

    Returns:
        str: A string representation of the dictionary, with each key-value pair on a new line in the format 'key = value'.

    Examples:
        >>> format_dict({'a': 1, 'b': "test"})
        'a = 1\nb = test\n'

        # NOTE: Strings are not quoted
        >>> print(format_dict({'a': "1", 'b': "test"}))
        a = 1
        b = test

        # NOTE: Nested dictionaries are printed in native dict/JSON format
        >>> print(format_dict({'a': "this", 'b': {"b1": 1, "b2": 2}}))
        a = this
        b = {'b1': 1, 'b2': 2}

        >>> format_dict({})
        ''
    """

    dict_str = ''

    for key, value in dictionary.items():
        dict_str += f'{key} = {value}\n'

    return dict_str

# --------------------------------------------------------------------------------------------------


def indent_lines(string: str, level: int = 0, reset: bool = False):
    """Indent and/or reset string lines by multiple of level

    Arguments:
    string: String to indent
    level: multiple of indentation
    reset: boolean of whether or not to reset string indentation
    """

    if reset:
        string = textwrap.dedent(string)

    string = textwrap.indent(string, INDENT*level) + '\n'

    return string

# --------------------------------------------------------------------------------------------------


class CylcSection():
    '''
    Holds the information contained in a section, including the name and contents, which can be a
    string or dictionary. Also tracks child subsections, automatically handling indentation
    and syntax at the time when the string is retrieved.

    Attributes:
    name: Header name of section
    content: String or mapping of cylc section content
    subsections: tracking of additional subsections to append to the section content
    '''

    def __init__(self, name: Optional[str] = None, content: Union[str, dict] = '') -> None:
        self.name = name
        self.content = content

        self.subsections = []

    def format_section(self, section: Self, level: int = 0) -> str:
        # Format a string to match cylc's section syntax
        # format the header with the appropriate amount of enclosing brackets and indents

        section_str = ''

        name = section.name
        if name is not None:
            section_str += textwrap.indent(f'{(level+1)*"["}{name}{"]"*(level+1)}\n', INDENT*level)
        else:
            level -= 1

        content = section.content
        if isinstance(content, Mapping):
            content = format_dict(content)

        section_str += indent_lines(content, level+1)

        return section_str

    def add_subsection(self, subsection: Self) -> None:
        """Add subsection to section tracking.
        
        Arguments:
        subsection: CylcSection object to append
        """
        self.subsections.append(subsection)

    def get_section_str(self, level: int = 0) -> str:
        """Get string of section contents for flow.cylc

        Arguments:
        level: int of indent level multiple

        Returns:
        String of section content
        """
        section_str = self.format_section(self, level)

        for subsection in self.subsections:
            section_str += subsection.get_section_str(level+1)

        if level == 0:
            section_str += f'# {"-"*98}\n\n'

        return section_str


# --------------------------------------------------------------------------------------------------
