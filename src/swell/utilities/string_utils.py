# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import re
import string


# --------------------------------------------------------------------------------------------------


def replace_vars(s, **defs):
    """Interpolate/replace variables in string

    Resolved variable formats are: $var, {{var}} and $(var). Undefined
    variables remain unchanged in the returned string. This method will
    recursively resolve variables of variables.

    Parameters
    ----------
    s : string, required
        Input string containing variables to be resolved.
    defs: dict, required
        dictionary of definitions for resolving variables expressed
        as key-word arguments.

    Returns
    -------
    s_interp: string
        Interpolated string. Undefined variables are left unchanged.
    """

    expr = s

    # Resolve special variables: {{var}}
    for var in re.findall(r'{{(\w+)}}', expr):
        if var in defs:
            expr = re.sub(r'{{'+var+r'}}', defs[var], expr)

    # Resolve special variables: $(var)
    for var in re.findall(r'\$\((\w+)\)', expr):
        if var in defs:
            expr = re.sub(r'\$\('+var+r'\)', defs[var], expr)

    # Resolve special variables: $[var] (list)
    for var in re.findall(r'\$\[(\w+)\]', expr):
        if var in defs:
            list2str = ','.join(map(str,defs[var]))
            expr = re.sub(r'\$\['+var+r'\]', '['+list2str+']', expr)

    # Resolve defs
    s_interp = string.Template(expr).safe_substitute(defs)

    # Recurse until no substitutions remain
    if s_interp != s:
        s_interp = replace_vars(s_interp, **defs)

    return s_interp

# --------------------------------------------------------------------------------------------------
