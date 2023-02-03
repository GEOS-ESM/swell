# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import jinja2
import yaml


# --------------------------------------------------------------------------------------------------


def template_string_jinja2(logger, templated_string, dictionary_of_templates):

    # Load the templated string
    t = jinja2.Template(templated_string, trim_blocks=True, lstrip_blocks=True,
                        undefined=jinja2.StrictUndefined)

    # Render the templates using the dictionary
    string_rendered = t.render(dictionary_of_templates)

    logger.assert_abort('{{' not in string_rendered, f'In use_config_to_template_string ' +
                        f'the output string still contains template directives. ' +
                        f'{string_rendered}')

    logger.assert_abort('}}' not in string_rendered, f'In use_config_to_template_string ' +
                        f'the output string still contains template directives. ' +
                        f'{string_rendered}')

    return string_rendered


# --------------------------------------------------------------------------------------------------
