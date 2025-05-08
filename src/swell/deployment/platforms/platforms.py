# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import importlib
import os
import yaml
from enum import Enum
import subprocess
import platform as pltfrm
from typing import Self

from importlib import resources

from swell.swell_path import get_swell_path


# --------------------------------------------------------------------------------------------------


def platform_path() -> str:

    return os.path.join(get_swell_path(), 'deployment', 'platforms')


# --------------------------------------------------------------------------------------------------


def login_or_compute(platform) -> str:

    '''
    Determine if running on login or compute node
    '''

    # Start by constructing the full platforms path
    platform_path = f"swell.deployment.platforms.{platform}"

    # Import the path dynamically
    try:
        path_import = importlib.import_module(platform_path)
    except ModuleNotFoundError:
        raise Exception(f"Platform '{platform}' has not been configured in SWELL")
    except Exception as err:
        raise err

    # Open the properties file
    properties_file = resources.files(path_import).joinpath('properties.yaml')
    with properties_file.open('r') as yaml_file:
        properties = yaml.safe_load(yaml_file)

    # If properties file does not exist return login to be safe
    if not os.path.exists(properties_file):
        return 'login'

    # Query the hostname by issuing shell command hostname
    hostname = os.popen('hostname').read().strip()

    if properties['hostname']['login'] in hostname:
        return 'login'
    elif properties['hostname']['compute'] in hostname:
        return 'compute'

    # Fallback to returning login to be safe
    return 'login'


# --------------------------------------------------------------------------------------------------


class SwellPlatforms(Enum):
    ''' Track platforms supported by Swell. '''
    NCCS_DISCOVER_SLES15 = 'nccs_discover_sles15'
    NCCS_DISCOVER_CASCADE = 'nccs_discover_cascade'
    AWS = 'aws'

    @classmethod
    def detect_platform(cls):
        ''' Detect the current platform, or return generic. '''

        # Try to get the hostname
        hostname = os.environ.get('HOSTNAME')
        os_name = pltfrm.platform()

        if hostname is not None:

            # Check for Discover hostnames
            if any(key in hostname for key in ['discover', 'borg', 'warp']):

                try:
                    # Try the lscpu shell command, which should be available across NCCS
                    cpu_info = str(subprocess.run('lscpu', capture_output=True).stdout)

                    model_name = cpu_info.split('Model name:')[1].strip().split('\n')[0].strip()

                except (FileNotFoundError, IndexError):
                    raise ValueError('NCCS Discover hostname detected, but failed to '
                                     'automatically detect cpu type with "lscpu".')

                # Match the cpu to the expected platform
                if all(key in model_name for key in ['Intel', 'Xeon']):
                    return cls.NCCS_DISCOVER_CASCADE
                elif all(key in model_name for key in ['AMD', 'EPYC']):
                    return cls.NCCS_DISCOVER_SLES15
                else:
                    raise ValueError(f'NCCS Discover hostname detected, but CPU model '
                                     f'{model_name} does not match any known node types')

        # Check for AWS
        if all(key in os_name for key in ['Linux', 'aws']):
            return cls.AWS

        raise ValueError(f'Unknown or unsupported platform: {os_name}.')

    # --------------------------------------------------------------------------------------------------

    @classmethod
    def get_all(cls) -> list:
        return [item.value for item in cls]

    # --------------------------------------------------------------------------------------------------

    @classmethod
    def match_name(cls, name: str) -> Self:
        # Return the enum instance based on the name
        return getattr(cls, name.upper())


# --------------------------------------------------------------------------------------------------
