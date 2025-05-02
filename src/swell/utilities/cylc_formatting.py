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
    dict_str = ''

    for key, value in dictionary.items():
        dict_str += f'{key} = {value}\n'

    return dict_str

def indent_lines(string: str, level: int = 0):
    out_string = ''

    for line in string.split('\n'):
        line = line.strip()

        if len(line) > 0:
            line = f'{indent*level}{line}'

        out_string += f'{line}\n'
    
    return out_string

class CylcSection():
    def __init__(self, name: Optional[str] = None, content: Union[str, dict] = '', level: int = 0) -> None:
        self.name = name
        self.content = content
        self.level = level
        print(name)
        print(content)
        self.section_str = self.__format_section__(self.name, self.content, self.level)

    def __format_section__(self, name: Optional[str] = None, content: Union[str, dict] = '', level: int = 0) -> str:
        section_str = ''
        print(level)
        if name is not None:
            section_str += f'{level*"["}{name}{"]"*level}\n'
        else:
            level -= 1

        if isinstance(content, Mapping):
            content = format_dict(content)

        section_str += indent_lines(content, level+1)

        if level == 0:
            section_str += f'# {"-"*98}\n'

        return section_str
    
    def add_subsection(self, subsection: Self):
        self.section_str += subsection.__format_section__(subsection.name, subsection.content, self.level+1)

    def get_section_str(self):
        return self.section_str

# --------------------------------------------------------------------------------------------------
