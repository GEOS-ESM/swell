# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import click
from typing import Union, Optional, Literal
import subprocess
import os

from swell.swell_path import get_swell_path
from swell.deployment.platforms.platforms import get_platforms

# --------------------------------------------------------------------------------------------------

def main(*args):
    opt = '/discover/nobackup/projects/gmao/advda/swell/dev/core/cylc/sles15_8.4.0/'
    env = {'PATH': os.path.join(opt, 'bin'),
           'PYTHONPATH': os.path.join(opt, 'lib', 'python3.11', 'site-packages'),
           'CYLC_PYTHONPATH': os.path.join(opt, 'lib', 'python3.11', 'site-packages')
           }

    cylc_command = 'cylc '
    for arg in args:
        cylc_command += f' {arg}'

    subprocess.run(cylc_command, env=env)


