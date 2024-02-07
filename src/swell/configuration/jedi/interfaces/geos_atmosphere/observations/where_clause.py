#!/usr/bin/env python3
"""
Update where clauses without changing yaml order
"""


import sys
import re
import pathlib

WHERE_CLAUSE_LINE = {"is_defined:.*": "value: is_valid",
                     "is_not_defined:.*": "value: is_not_valid",
                     "is_true:.*": "value: is_true",
                     "is_false:.*": "value: is_false",
                     }


def replace_where_clauses(path):
    with open(path, "r") as fp:
        content = fp.read()

    for current, new_clause in WHERE_CLAUSE_LINE.items():
        if re.search(current, content):
            content = re.sub(current, new_clause, content)

    with open(path, "w") as fp:
        fp.write(content)


def main():

    # walk all files starting from current directory
    root = pathlib.Path()

    files = (
        [fl for fl in root.glob("**/*.yaml") if fl.is_file()]
    )

    for file_path in files:
        print(f"Replacing where clauses in: {file_path}")
        replace_where_clauses(file_path)


if __name__ == "__main__":
    main()

