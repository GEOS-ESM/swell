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
    A custom undefined class that doesn't raise errors when variables are missing and handles
    nested structures by returning another instance of SilentUndefined if an attribute or item
    is missing.
    """
    def __str__(self):
        try:
            # Attempt to render the placeholder as it was in the template
            return f'{{{{ {self._undefined_name} }}}}'
        except AttributeError:
            # Fallback in case the name isn't set
            return self._undefined_hint or self._undefined_obj

    def __unicode__(self):
        return str(self)

    def __getattr__(self, name):
        return SilentUndefined()

    def __getitem__(self, name):
        return SilentUndefined()


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
        logger.abort(f'Resolving templates for templated_string failed with the following '
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
