# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.utilities.logger import Logger

# --------------------------------------------------------------------------------------------------
# R2D2 Model Name Mapping
# --------------------------------------------------------------------------------------------------
# To add a new model:
#   1. Register the model in R2D2 (with r2d2.register_model())
#   2. Add it to the dictionary below

R2D2_MODEL_MAP = {
    'geos_atmosphere': 'geos',
    'geos_marine': 'mom6',
}


def get_r2d2_model_name(swell_model):
    return R2D2_MODEL_MAP.get(swell_model, swell_model)


# Lifetime is set when registering an experiment with r2d2.register_experiment(),
# All data stored under an experiment inherits its lifetime.
#
# Valid values:
#   - 'debug':       Short-term
#   - 'science':     Medium-term
#   - 'publication': Long-term
#   - 'release':     Permanent
#
# Ex: r2d2.register_experiment(name='exp_name', ..., lifetime='science')
# --------------------------------------------------------------------------------------------------


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
            with open(yaml_path, 'r') as yaml_file:
                credentials = yaml.safe_load(yaml_file)
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

    # Set host and compiler (YAML config takes precedence over platform detection)
    if 'host' in credentials and 'R2D2_HOST' not in os.environ:
        os.environ['R2D2_HOST'] = credentials['host']
        logger.info(f"Using platform host '{r2d2_host}' (overriding YAML '{credentials['host']}')")
        logger.warning("Using host from YAML file")

    elif r2d2_host and 'R2D2_HOST' not in os.environ:
        os.environ['R2D2_HOST'] = r2d2_host
        logger.info(f"Set R2D2_HOST={r2d2_host} from platform configuration")

    # Set compiler
    if 'compiler' in credentials and 'R2D2_COMPILER' not in os.environ:
        os.environ['R2D2_COMPILER'] = credentials['compiler']
        logger.info(f"Using platform compiler '{r2d2_compiler}' \
                    (overriding YAML '{credentials['compiler']}')")
        logger.warning("Using compiler from YAML file")

    elif r2d2_compiler and 'R2D2_COMPILER' not in os.environ:
        os.environ['R2D2_COMPILER'] = r2d2_compiler
        logger.info(f"Set R2D2_COMPILER={r2d2_compiler} from platform configuration")

    logger.info("R2D2 v3 credentials loaded successfully")


# ----------------------------------------------------------------------------------------------
