# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import subprocess
import os
import sys

from swell.deployment.platforms.platforms import SwellPlatform
from swell.utilities.logger import Logger

# --------------------------------------------------------------------------------------------------


def configure_cylc_environment(append_dict: dict = {}) -> dict:
    ''' Unset the path containing Swell's cylc entry point, and set
        the environment according to the specified dictionary '''

    env_dict = os.environ

    env_path = os.environ.get('PATH')
    if env_path is None:
        env_path = ''

    cylc_exec = subprocess.run(['which', 'cylc'], capture_output=True).stdout.decode()
    current_cylc_path = os.path.normpath(cylc_exec.split('cylc')[0])

    if os.path.exists(current_cylc_path):
        if current_cylc_path in env_path:
            env_path = env_path.replace(current_cylc_path, '')

    env_dict['PATH'] = env_path

    for key, value in append_dict.items():
        field = value
        if key in env_dict.keys():
            field = env_dict[key] + ':' + field

        env_dict[key] = field
    return env_dict


# --------------------------------------------------------------------------------------------------

def execute_cylc(argv=sys.argv) -> None:
    ''' Custom entry point for Cylc on Discover. '''

    logger = Logger('SwellCylcEntryPoint')

    platform = SwellPlatform.detect_platform()

    # Location for Discover cylc installation
    if platform in [SwellPlatform.NCCS_DISCOVER_CASCADE, SwellPlatform.NCCS_DISCOVER_SLES15]:
        opt = '/discover/nobackup/projects/gmao/advda/swell/dev/core/cylc/sles15_8.4.0/'
        python_ver = 'python3.11'

        append_env = {'PATH': os.path.join(opt, 'bin'),
                      'PYTHONPATH': os.path.join(opt, 'lib', python_ver, 'site-packages'),
                      'CYLC_PYTHONPATH': os.path.join(opt, 'lib', python_ver, 'site-packages')}

        # Point directly to cylc installation
        cylc_command = [os.path.join(opt, 'bin', 'cylc')] + argv[1:]

        env = configure_cylc_environment(append_env)

        subprocess.run(cylc_command, env=env)

    # Try just calling cylc from the path
    else:
        cylc_command = ['cylc'] + argv[1:]

        logger.warning('Platform not recognized, attempting to call Cylc executable from the path.')
        logger.warning('Cylc must be installed for this to work.')

        env = configure_cylc_environment()

        subprocess.run(cylc_command, env=env)

# --------------------------------------------------------------------------------------------------
