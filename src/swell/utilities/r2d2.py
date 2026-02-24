# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
from ruamel.yaml import YAML

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

    # Load R2D2 v3 credentials from ~/.swell/r2d2_credentials.yaml
    # -----------------------------------------------------------
    load_r2d2_credentials(logger, platform)

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


def _get_platform_r2d2_config(logger: Logger, platform: str = None) -> tuple:
    if not platform:
        logger.info("No platform specified, cannot determine R2D2 host/compiler")
        return None, None

    # Platform-specific R2D2 configurations
    platform_configs = {
        'nccs_discover_sles15': {
            'host': 'discover-gmao',
            'compiler': 'intel'
        },
        'nccs_discover_cascade': {
            'host': 'discover-gmao',
            'compiler': 'intel'
        },
        'aws': {
            'host': 'aws-gmao',
            'compiler': 'intel'  # or 'gnu' depending on AWS setup
        },
        'generic': {
            'host': None,
            'compiler': None
        }
    }

    if platform in platform_configs:
        config = platform_configs[platform]
        logger.info(f"Using R2D2 configuration for platform \
                    '{platform}': host={config['host']}, \
                    compiler={config['compiler']}")
        return config['host'], config['compiler']
    else:
        logger.warning(f"Unknown platform '{platform}', cannot determine R2D2 host/compiler")
        return None, None


def load_r2d2_credentials(
    logger: Logger,
    platform: str = None,
    yaml_path: str = "~/.swell/r2d2_credentials.yaml"
) -> None:
    """
    Load R2D2 v3 credentials from YAML file and set environment variables.
    Host and compiler are automatically determined from platform configuration or YAML file.

    Args:
        logger: SWELL logger instance
        platform: Platform name (e.g., 'nccs_discover_sles15')
        yaml_path: Path to R2D2 credentials YAML file
    """
    yaml_path = os.path.expanduser(yaml_path)

    # Determine platform-specific host and compiler
    r2d2_host, r2d2_compiler = _get_platform_r2d2_config(logger, platform)

    # Load credentials from YAML file if it exists
    credentials = {}
    if os.path.exists(yaml_path):
        logger.info(f"Loading R2D2 v3 credentials from {yaml_path}")
        try:
            yaml = YAML(typ='safe')
            with open(yaml_path, 'r') as yaml_file:
                credentials = yaml.load(yaml_file)
        except Exception as e:
            logger.error(f"Error loading R2D2 credentials from {yaml_path}: {e}")
            logger.info("Continuing with existing environment variables...")
            credentials = {}
    else:
        logger.info(f"R2D2 credentials file not found at {yaml_path}")
        logger.info("R2D2 v3 will use existing environment variables if set")

    # Set user credentials from YAML file
    if 'user' in credentials and 'R2D2_USER' not in os.environ:
        os.environ['R2D2_USER'] = credentials['user']

    if 'api_key' in credentials and 'R2D2_API_KEY' not in os.environ:
        os.environ['R2D2_API_KEY'] = credentials['api_key']

    if 'r2d2_server_host' in credentials and 'R2D2_HOST' not in os.environ:
        os.environ['R2D2_SERVER_HOST'] = credentials['r2d2_server_host']
    
    if 'r2d2_server_port' in credentials and 'R2D2_SERVER_PORT' not in os.environ:
        os.environ['R2D2_SERVER_PORT'] = str(credentials['r2d2_server_port'])
    
    if 'aws_access_key_id' in credentials and 'AWS_ACCESS_KEY_ID' not in os.environ:
        os.environ['AWS_ACCESS_KEY_ID'] = credentials['aws_access_key_id']
    
    if 'aws_secret_access_key' in credentials and 'AWS_SECRET_ACCESS_KEY' not in os.environ:
        os.environ['AWS_SECRET_ACCESS_KEY'] = credentials['aws_secret_access_key']

    if 'aws_session_token' in credentials and 'AWS_SESSION_TOKEN' not in os.environ:
        os.environ['AWS_SESSION_TOKEN'] = credentials['aws_session_token']

    # Set host and compiler (YAML config takes precedence over platform detection)
    if 'r2d2_host' in credentials and 'R2D2_HOST' not in os.environ:
        os.environ['R2D2_HOST'] = credentials['r2d2_host']
        logger.info(f"Using platform host '{r2d2_host}' (overriding YAML '{credentials['r2d2_host']}')")
        logger.warning("Using host from YAML file")

    elif r2d2_host and 'R2D2_HOST' not in os.environ:
        os.environ['R2D2_HOST'] = r2d2_host
        logger.info(f"Set R2D2_HOST={r2d2_host} from platform configuration")

    # Set compiler
    if 'r2d2_compiler' in credentials and 'R2D2_COMPILER' not in os.environ:
        os.environ['R2D2_COMPILER'] = credentials['r2d2_compiler']
        logger.info(f"Using platform compiler '{r2d2_compiler}' \
                    (overriding YAML '{credentials['r2d2_compiler']}')")
        logger.warning("Using compiler from YAML file")

    elif r2d2_compiler and 'R2D2_COMPILER' not in os.environ:
        os.environ['R2D2_COMPILER'] = r2d2_compiler
        logger.info(f"Set R2D2_COMPILER={r2d2_compiler} from platform configuration")

    logger.info("R2D2 v3 credentials loaded successfully")


# ----------------------------------------------------------------------------------------------
