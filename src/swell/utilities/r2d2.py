# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
from ruamel.yaml import YAML
import random
import subprocess

from swell.utilities.logger import Logger

# --------------------------------------------------------------------------------------------------
# R2D2 Model Name Mapping
# --------------------------------------------------------------------------------------------------
# To add a new model:
#   1. Register the model in R2D2 (with r2d2.register_model())
#   2. Add it to the dictionary below

R2D2_MODEL_MAP = {
    'geos_atmosphere': ['geos'],
    'geos_marine': ['mom6', 'cice6'],
    'geos_cf': ['geos_cf'],
}

# Platform-specific R2D2 module config
_R2D2_MODULE_CONFIG = {
    'nccs_discover_sles15': {
        'module_path': '/discover/nobackup/projects/gmao/advda/JediOpt/modulefiles/core',
        'module_name': 'r2d2-client/112025',
    },
    'nccs_discover_cascade': {
        'module_path': '/discover/nobackup/projects/gmao/advda/JediOpt/modulefiles/core',
        'module_name': 'r2d2-client/112025',
    },
}

# --------------------------------------------------------------------------------------------------


def load_r2d2_module(logger: Logger, platform: str) -> None:
    """Load R2D2 module via bash, capture env, apply to current process."""
    if platform not in _R2D2_MODULE_CONFIG:
        return
    config = _R2D2_MODULE_CONFIG[platform]
    cmd = (
        f'source /usr/share/lmod/lmod/init/bash && '
        f'module use -a {config["module_path"]} && '
        f'module load {config["module_name"]} && env'
    )
    try:
        result = subprocess.run(['bash', '-c', cmd], capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            logger.warning(f'Failed to load R2D2 module: {result.stderr}')
            return
        for line in result.stdout.strip().split('\n'):
            if '=' in line:
                key, _, value = line.partition('=')
                os.environ[key] = value
                # PYTHONPATH needs to be added to sys.path for import to work
                if key == 'PYTHONPATH':
                    import sys
                    for p in value.split(':'):
                        if p and p not in sys.path:
                            sys.path.insert(0, p)
        logger.info(f'Loaded R2D2 module: {config["module_name"]}')
    except Exception as e:
        logger.warning(f'Could not load R2D2 module: {e}')

# ----------------------------------------------------------------------------------------------


def get_r2d2_models(swell_model):
    """Returns list of all R2D2 model names."""
    models = R2D2_MODEL_MAP.get(swell_model, [swell_model])
    return models if isinstance(models, list) else [models]


def get_r2d2_model_name(swell_model):
    """Returns the first R2D2 model name."""
    return get_r2d2_models(swell_model)[0]


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

# --------------------------------------------------------------------------------------------------


def _get_platform_r2d2_config(logger: Logger, platform: str = None) -> tuple:
    if not platform:
        logger.info("No platform specified, cannot determine R2D2 host/compiler")
        return None, None

    # Platform-specific R2D2 configurations
    # Note: ~/.swell/r2d2_credentials.yaml overrides these values if specified
    platform_configs = {
        'nccs_discover_sles15': {
            'host': 'discover-gmao',
            'compiler': 'intel'
        },
        'nccs_discover_cascade': {
            'host': 'discover-gmao',
            'compiler': 'intel'
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

# --------------------------------------------------------------------------------------------------


def load_r2d2_credentials(
    logger: Logger,
    platform: str = None,
    yaml_path: str = "~/.swell/r2d2_credentials.yaml",
    r2d2_server: str | None = None,
) -> None:
    """
    Load R2D2 credentials from YAML file and set environment variables.
    Host and compiler are automatically determined from platform configuration or YAML file.

    Args:
        logger: SWELL logger instance
        platform: Platform name (e.g., 'nccs_discover_sles15')
        yaml_path: Path to R2D2 credentials YAML file
        r2d2_server: Server/profile name in the credentials YAML
            (e.g. 'gmao', 'jcsda'). Selects which named credential block to load.
            If not set, uses ``R2D2_SERVER`` env var if available.
            If neither is set, uses the root of the YAML file.
    """
    yaml_path = os.path.expanduser(yaml_path)

    server_name = None if r2d2_server is None else str(r2d2_server).strip() or None
    if server_name is None:
        env_server_name = os.environ.get('R2D2_SERVER')
        if isinstance(env_server_name, str):
            server_name = env_server_name.strip() or None

    # Determine platform-specific host and compiler
    r2d2_host, r2d2_compiler = _get_platform_r2d2_config(logger, platform)

    # Load credentials from YAML file if it exists
    credentials_yaml = {}
    if os.path.exists(yaml_path):
        logger.info(f"Loading R2D2 credentials from {yaml_path}")
        try:
            yaml = YAML(typ='safe')
            with open(yaml_path, 'r') as yaml_file:
                credentials_yaml = yaml.load(yaml_file) or {}
        except Exception as e:
            logger.error(f"Error loading R2D2 credentials from {yaml_path}: {e}")
            logger.info("Continuing with existing environment variables...")
            credentials_yaml = {}
    else:
        logger.info(f"R2D2 credentials file not found at {yaml_path}")
        logger.info("R2D2 will use existing environment variables if set")

    if not isinstance(credentials_yaml, dict):
        raise TypeError("R2D2 credentials file must contain a YAML mapping at the root.")

    if server_name is not None:
        server_credentials = credentials_yaml.get(server_name)
        if isinstance(server_credentials, dict):
            credentials = server_credentials
            logger.info(f"Using R2D2 credentials for server: {server_name!r}")
        else:
            raise ValueError(
                f"R2D2 credentials for server {server_name!r} not found or not a mapping."
            )
    else:
        # Select the first server name
        all_named = bool(credentials_yaml) and all(
            isinstance(v, dict) for v in credentials_yaml.values()
        )
        if all_named:
            server_name = next(iter(credentials_yaml))
            credentials = credentials_yaml[server_name]
            logger.info(f"No r2d2_server set, auto-selected first profile: {server_name!r}")
        else:
            credentials = credentials_yaml

    # Set user credentials from YAML file
    if 'user' in credentials and 'R2D2_USER' not in os.environ:
        os.environ['R2D2_USER'] = credentials['user']

    if 'api_key' in credentials and 'R2D2_API_KEY' not in os.environ:
        os.environ['R2D2_API_KEY'] = credentials['api_key']

    if 'r2d2_server_host' in credentials and 'R2D2_SERVER_HOST' not in os.environ:
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
        logger.info(
            f"YAML r2d2_host ({credentials['r2d2_host']!r}) overrides "
            f"platform default ({r2d2_host!r})"
        )

    elif r2d2_host and 'R2D2_HOST' not in os.environ:
        os.environ['R2D2_HOST'] = r2d2_host
        logger.info(f"Set R2D2_HOST={r2d2_host} from platform configuration")

    # Set compiler
    if 'r2d2_compiler' in credentials and 'R2D2_COMPILER' not in os.environ:
        os.environ['R2D2_COMPILER'] = credentials['r2d2_compiler']
        logger.info(
            f"YAML r2d2_compiler ({credentials['r2d2_compiler']!r}) overrides "
            f"platform default ({r2d2_compiler!r})"
        )

    elif r2d2_compiler and 'R2D2_COMPILER' not in os.environ:
        os.environ['R2D2_COMPILER'] = r2d2_compiler
        logger.info(f"Set R2D2_COMPILER={r2d2_compiler} from platform configuration")

    # Set custom server connection (only needed for non-JCSDA servers)
    if 'server_host' in credentials and 'R2D2_SERVER_HOST' not in os.environ:
        os.environ['R2D2_SERVER_HOST'] = credentials['server_host']
        logger.info(f"Set R2D2_SERVER_HOST={credentials['server_host']} from credentials file")

    if 'server_port' in credentials and 'R2D2_SERVER_PORT' not in os.environ:
        os.environ['R2D2_SERVER_PORT'] = str(credentials['server_port'])
        logger.info(f"Set R2D2_SERVER_PORT={credentials['server_port']} from credentials file")

    logger.info("R2D2 v3 credentials loaded successfully")

# ----------------------------------------------------------------------------------------------


def random_hex_id(swell_id: str, length: int = 8):
    return f"{swell_id}-{random.randrange(16**length):0{length}x}"

# ----------------------------------------------------------------------------------------------


def experiment_exists(r2d2_id: str):
    import r2d2

    try:
        r2d2.get(item='experiment', name=r2d2_id)
        return True
    except Exception as e:
        err = str(e)
        if '400 Client Error' in err or '404 Not Found' in err or '404 Client Error' in err:
            return False
        raise

# ----------------------------------------------------------------------------------------------


def unique_r2d2_id(swell_id: str, platform: str) -> str:

    # Just use the ID if it doesn't exist
    if not experiment_exists(swell_id):
        return swell_id

    # If not, append an unused hex id
    # Only try this 10 times
    for i in range(10):
        temp_id = random_hex_id(swell_id, length=8)
        if not experiment_exists(temp_id):
            return temp_id

    raise Exception('Could not find a valid experiment_id for R2D2')

# --------------------------------------------------------------------------------------------------
