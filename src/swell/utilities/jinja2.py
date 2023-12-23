# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import jinja2


# --------------------------------------------------------------------------------------------------


def template_string_jinja2(logger, templated_string, dictionary_of_templates,
                           allow_unresolved=False):

    # Undefined
    undefined = jinja2.StrictUndefined
    if allow_unresolved:
        undefined = jinja2.Undefined

    # Load the templated string
    t = jinja2.Template(templated_string, trim_blocks=True, lstrip_blocks=True,
                        undefined=undefined)

    # Render the templates using the dictionary
    string_rendered = t.render(dictionary_of_templates)

    # Extra safety checks
    if not allow_unresolved:
        logger.assert_abort('{{' not in string_rendered, f'In template_string_jinja2 ' +
                            f'the output string still contains template directives. ' +
                            f'{string_rendered}')

        logger.assert_abort('}}' not in string_rendered, f'In template_string_jinja2 ' +
                            f'the output string still contains template directives. ' +
                            f'{string_rendered}')

    return string_rendered


# --------------------------------------------------------------------------------------------------
