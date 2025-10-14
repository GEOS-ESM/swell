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


def map_r2d2_v3_to_v1_params(v3_params: dict) -> dict:
    """
    Map R2D2 v3 parameters to R2D2 v1 parameters for fallback.
    """

    v1_params = {}
    
    # Map item types - only feedback needs special handling
    if 'item' in v3_params:
        if v3_params['item'] == 'feedback':
            v1_params['type'] = 'ob'  # v1 uses 'ob' for observations
        else:
            v1_params['type'] = v3_params['item']
    
    if 'observation_type' in v3_params:
        v1_params['obs_type'] = v3_params['observation_type']
    
    if 'window_start' in v3_params:
        v1_params['date'] = v3_params['window_start']
    elif 'date' in v3_params:
        v1_params['date'] = v3_params['date']
    
    if 'window_length' in v3_params:
        v1_params['time_window'] = v3_params['window_length']
    
    # Map other parameters 
    direct_mapping = ['provider', 'experiment', 'model', 'resolution', 'step', 'member']
    for param in direct_mapping:
        if param in v3_params:
            v1_params[param] = v3_params[param]
    
    # Add required v1 parameters that might be missing
    if 'ignore_missing' not in v1_params:
        v1_params['ignore_missing'] = True
    
    return v1_params


def _load_r2d2_v1_modules():
    import subprocess
    import sys
    
    module_commands = [
        "module use -a /discover/nobackup/projects/gmao/advda/JediOpt/modulefiles/core",
        "module load r2d2/sles15_spack19"
    ]
    
    # Execute module commands
    for cmd in module_commands:
        try:
            result = subprocess.run(f"bash -c 'source /usr/share/lmod/lmod/init/bash && {cmd}'", 
                                  shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Warning: Failed to execute {cmd}: {result.stderr}")
        except Exception as e:
            print(f"Warning: Error loading R2D2 v1 modules: {e}")


def r2d2_fetch_with_fallback(logger: Logger, **kwargs) -> bool:
    """
    Fetch data using R2D2 v3 first, fallback to v1 if needed.
    """
    
    # Keep target_file in kwargs for v3
    target_file = kwargs.get('target_file', None)
    if not target_file:
        logger.error("target_file parameter is required")
        return False
    
    # Try R2D2 v3 first
    try:
        logger.info(f"Attempting R2D2 v3 fetch for {target_file}")
        import r2d2
        
        # R2D2 v3 needs all parameters including target_file
        r2d2.fetch(**kwargs)

        logger.info(f"Successfully fetched {target_file} using R2D2 v3")
        return True
        
    except Exception as e:
        logger.warning(f"R2D2 v3 fetch failed: {str(e)}")
        logger.info("Attempting fallback to R2D2 v1...")
        
        # Try R2D2 v1 fallback
        try:
            # Map v3 parameters to v1
            v1_params = map_r2d2_v3_to_v1_params(kwargs)
            
            # Load R2D2 v1 modules dynamically
            _load_r2d2_v1_modules()
            
            import sys
            if 'r2d2' in sys.modules:
                del sys.modules['r2d2']
            
            # Import R2D2 v1 functions
            from r2d2 import fetch as fetch_v1
            
            logger.info(f"Attempting R2D2 v1 fetch with parameters: {v1_params}")
            fetch_v1(target_file=target_file, **v1_params)
            logger.info(f"Successfully fetched {target_file} using R2D2 v1 fallback")
            return True
            
        except Exception as e2:
            logger.error(f"R2D2 v1 fallback also failed: {str(e2)}")
            logger.error(f"Failed to fetch {target_file} using both R2D2 v3 and v1")
            return False


def r2d2_store_with_fallback(logger: Logger, source_file: str, **kwargs) -> bool:
    # Try R2D2 v3 first
    try:
        logger.info(f"Attempting R2D2 v3 store for {source_file}")
        import r2d2
        r2d2.store(source_file=source_file, **kwargs)
        logger.info(f"Successfully stored {source_file} using R2D2 v3")
        return True
        
    except Exception as e:
        logger.warning(f"R2D2 v3 store failed: {str(e)}")
        logger.info("Attempting fallback to R2D2 v1...")
        
        # Try R2D2 v1 fallback
        try:
            # Map v3 parameters to v1
            v1_params = map_r2d2_v3_to_v1_params(kwargs)
            
            # Load R2D2 v1 modules dynamically
            _load_r2d2_v1_modules()
            
            # Clear Python module cache to force reload
            import sys
            if 'r2d2' in sys.modules:
                del sys.modules['r2d2']
            
            # Import R2D2 v1 functions
            from r2d2 import store as store_v1
            
            logger.info(f"Attempting R2D2 v1 store with parameters: {v1_params}")
            store_v1(source_file=source_file, **v1_params)
            logger.info(f"Successfully stored {source_file} using R2D2 v1 fallback")
            return True
            
        except Exception as e2:
            logger.error(f"R2D2 v1 fallback also failed: {str(e2)}")
            logger.error(f"Failed to store {source_file} using both R2D2 v3 and v1")
            return False


# ----------------------------------------------------------------------------------------------
