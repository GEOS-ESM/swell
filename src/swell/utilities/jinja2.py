# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import jinja2 as j2


# --------------------------------------------------------------------------------------------------


class SilentUndefined(j2.Undefined):
    """
    A custom undefined class that doesn't raise errors when variables are missing and returns the
    original template variable placeholder.
    """
    def __getattr__(self, name):
        # Return a new SilentUndefined instance but append the attribute access to the name.
        return SilentUndefined(name=f"{self._undefined_name}.{name}")

    def __getitem__(self, key):
        # Similar to __getattr__, return a new instance with the key access incorporated.
        if isinstance(key, str):
            return SilentUndefined(name=f"{self._undefined_name}['{key}']")
        return SilentUndefined(name=f"{self._undefined_name}[{key}]")

    def items(self):
        # Return an empty list when items method is called.
        return []

    def __str__(self):
        # Ensure the name returned reflects the original template placeholder.
        return f"{{{{ {self._undefined_name} }}}}"

    def __repr__(self):
        return str(self)


# --------------------------------------------------------------------------------------------------


def template_string_jinja2(logger, templated_string, dictionary_of_templates,
                           allow_unresolved=False):

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
        logger.assert_abort('{{' not in string_rendered, f'In template_string_jinja2 ' +
                            f'the output string still contains template directives. ' +
                            f'{string_rendered}')

        logger.assert_abort('}}' not in string_rendered, f'In template_string_jinja2 ' +
                            f'the output string still contains template directives. ' +
                            f'{string_rendered}')

    return string_rendered


# --------------------------------------------------------------------------------------------------
