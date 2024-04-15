# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


# standard imports
import os
import re
import glob

# swell imports
from swell.swell_path import get_swell_path
from swell.utilities.logger import Logger


# --------------------------------------------------------------------------------------------------


def main():

    # Create a logger
    logger = Logger('CheckJediInterfaceTemplates')

    config_types = ['oops/*yaml',
                    'interfaces/*/model/*yaml',
                    'interfaces/*/observations/*yaml',
                    'interfaces/*/model/geometry.yaml',
                    'interfaces/*/model/background.yaml',
                    'interfaces/*/model/background4D.yaml',
                    'interfaces/*/model/r2d2.yaml',
                    'interfaces/*/model/stage*.yaml',
                    'interfaces/*/model/background_error.yaml',
                    ]

    # Path to JEDI interface code
    swell_path = get_swell_path()
    jedi_interfaces_path = os.path.join(swell_path, 'configuration', 'jedi')

    # Default keys
    def_keys = ['experiment_id', 'experiment_root', 'model_component', 'cycle_dir']

    # Loop over config types
    for config_type in config_types:

        # Path to the files for this config type
        config_yaml_path = os.path.join(jedi_interfaces_path, config_type)

        config_yaml_files = glob.glob(config_yaml_path)

        # String to hold contents of all the files
        all_config_files_str = ''

        for config_yaml_file in config_yaml_files:

            with open(config_yaml_file, 'r') as file:
                file_lines = file.read().split('\n')

            # Rejoin with space between lines to eliminate new line deliminator
            all_config_files_str = all_config_files_str + ' '.join(file_lines)

        # Split again using space or slash
        all_config_files_lines = re.split(' |/', all_config_files_str)

        # Keep only elements with templates
        all_config_files_lines = [x for x in all_config_files_lines if "{{" in x]

        # Loop and find all instances of templates and add to list
        templates = []
        for all_config_files_line in all_config_files_lines:

            res = re.findall(r'\{\{.*?\}\}', all_config_files_line)
            templates = templates + res

        # Remove duplicates & sort
        templates = sorted(list(set(templates)))

        # Remove some keys
        for ind, template in enumerate(templates):
            templates[ind] = templates[ind].strip('{').strip('}')
            if templates[ind] in def_keys:
                templates[ind] = '*** ' + templates[ind]

        # Resort to gather ***
        templates = sorted(list(set(templates)))

        # Print the templates
        logger.info(config_type)
        logger.info('-'*len(config_type))
        for template in templates:
            logger.info(template)
        if config_type != config_types[-1]:
            logger.info(' ', False)


# --------------------------------------------------------------------------------------------------
