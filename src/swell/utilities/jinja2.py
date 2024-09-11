# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

from typing import Union

import jinja2 as j2

from swell.utilities.logger import Logger

# --------------------------------------------------------------------------------------------------


class SilentUndefined(j2.Undefined):
    """
    A custom undefined class that doesn't raise errors when variables are missing and returns the
    original template variable placeholder.

    In order to identify which tasks are used and to define questions for the CLI
    configuration method, two Jinja2 passes occur on each suite's flow.cylc files
    where "swell task" commands are defined. By design, first pass leaves most of
    the templates as is (non-exhaustive). Hence, this class ensures that we ignore
    the exceptions defined here, silently.

    See `ask_questions_and_configure_suite` method in `prepare_config_and_suite.py`
    for more details on Jinja2 passes.
    """
    def __getattr__(self, name: str) -> 'SilentUndefined':
        # Return a new SilentUndefined instance but append the attribute access to the name.
        return SilentUndefined(name=f"{self._undefined_name}.{name}")

    def __getitem__(self, key: Union[str, int]) -> 'SilentUndefined':
        # Similar to __getattr__, return a new instance with the key access incorporated.
        if isinstance(key, str):
            return SilentUndefined(name=f"{self._undefined_name}['{key}']")
        return SilentUndefined(name=f"{self._undefined_name}[{key}]")

    def items(self) -> list:
        # Return an empty list when items method is called.
        return []

    def __str__(self) -> str:
        # Ensure the name returned reflects the original template placeholder.
        return f"{{{{ {self._undefined_name} }}}}"

    def __repr__(self) -> str:
        return str(self)


# --------------------------------------------------------------------------------------------------


def template_string_jinja2(
    logger: Logger,
    templated_string: str,
    dictionary_of_templates: dict,
    allow_unresolved: bool = False
) -> str:

    # Handling of templates that cannot be resolved
    # ---------------------------------------------
    undefined = SilentUndefined if allow_unresolved else j2.StrictUndefined

    # Create the Jinja2 environment
    # -----------------------------
    env = j2.Environment(undefined=undefined)

    # Load the algorithm template
    # ---------------------------
    template = env.from_string(templated_string)

    # Render the template hierarchy
    # -----------------------------
    try:
        string_rendered = template.render(dictionary_of_templates)
    except j2.exceptions.UndefinedError as e:
        logger.abort('Resolving templates for templated_string failed with the following ' +
                     f'exception: {e}')

    # Extra safety checks
    # -------------------
    if not allow_unresolved:
        logger.assert_abort(
            not (('{{' in string_rendered) or ('}}' in string_rendered)),
            f"""
            In template_string_jinja2, the output string still contains template directives:
            '''
            {string_rendered}
            '''
            """
        )

    return string_rendered


# --------------------------------------------------------------------------------------------------
