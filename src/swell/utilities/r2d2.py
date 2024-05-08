# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os

from swell.swell_path import get_swell_path
from swell.utilities.jinja2 import template_string_jinja2

# --------------------------------------------------------------------------------------------------


def create_r2d2_config(logger, platform, cycle_dir, r2d2_local_path):

    # R2D2 config file that will be created
    r2d2_config_file = os.path.join(cycle_dir, 'r2d2_config.yaml')

    # Set the environment variable R2D2_CONFIG
    os.environ["R2D2_CONFIG"] = r2d2_config_file

    # If the file already exists then return
    if os.path.isfile(r2d2_config_file):
        return

    # Read R2D2 config file template that will be read
    r2d2_config_file_template = os.path.join(get_swell_path(), 'deployment', 'platforms', platform,
                                             'r2d2_config.yaml')

    with open(r2d2_config_file_template, 'r') as f:
        r2d2_config_file_template_str = f.read()

    # Create a dictionary containing r2d2_local_path
    r2d2_config_dict = {'r2d2_local_path': r2d2_local_path}

    # Replace the template with the dictionary
    r2d2_config_file_template_str = template_string_jinja2(logger, r2d2_config_file_template_str,
                                                           r2d2_config_dict)

    # Expand environment variables in templated file
    r2d2_config_file_template_str = os.path.expandvars(r2d2_config_file_template_str)

    # Write the config file
    with open(r2d2_config_file, 'w') as f:
        f.write(r2d2_config_file_template_str)


# ----------------------------------------------------------------------------------------------
