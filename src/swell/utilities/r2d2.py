# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.swell_path import get_swell_path
from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.logger import Logger

# --------------------------------------------------------------------------------------------------


def create_r2d2_config(
    logger: Logger,
    platform: str,
    cycle_dir: str,
    r2d2_local_path: str
) -> None:

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


def load_r2d2_credentials(
    logger: Logger,
    yaml_path: str = "~/.swell/r2d2_credentials.yaml"
) -> None:
    """
    Load R2D2 v3 credentials from YAML file and set environment variables.
    
    Args:
        logger: SWELL logger instance
        yaml_path: Path to R2D2 credentials YAML file
    """
    yaml_path = os.path.expanduser(yaml_path)
    
    if not os.path.exists(yaml_path):
        logger.info(f"R2D2 credentials file not found at {yaml_path}")
        logger.info("R2D2 v3 will use existing environment variables if set")
        return
    
    logger.info(f"Loading R2D2 v3 credentials from {yaml_path}")
    
    try:
        with open(yaml_path, 'r') as yaml_file:
            credentials = yaml.safe_load(yaml_file)
        
        # Set R2D2 v3 environment variables from config file
        if 'user' in credentials and 'R2D2_USER' not in os.environ:
            os.environ['R2D2_USER'] = credentials['user']
            
        if 'api_key' in credentials and 'R2D2_API_KEY' not in os.environ:
            os.environ['R2D2_API_KEY'] = credentials['api_key']
            
        if 'host' in credentials and 'R2D2_HOST' not in os.environ:
            os.environ['R2D2_HOST'] = credentials['host']
            
        if 'compiler' in credentials and 'R2D2_COMPILER' not in os.environ:
            os.environ['R2D2_COMPILER'] = credentials['compiler']
            
        logger.info("R2D2 v3 credentials loaded successfully")
        
    except Exception as e:
        logger.error(f"Error loading R2D2 credentials from {yaml_path}: {e}")
        logger.info("Continuing with existing environment variables...")


# ----------------------------------------------------------------------------------------------
