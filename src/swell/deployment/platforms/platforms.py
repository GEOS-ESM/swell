# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import yaml

from swell.swell_path import get_swell_path


# --------------------------------------------------------------------------------------------------


def platform_path() -> str:

    return os.path.join(get_swell_path(), 'deployment', 'platforms')


# --------------------------------------------------------------------------------------------------


def get_platforms() -> list:

    # Get list of supported platforms
    platforms = [dir for dir in os.listdir(platform_path())
                 if os.path.isdir(os.path.join(platform_path(), dir))]

    # If anything in platforms contains '__' remove it from platforms list
    platforms = [platform for platform in platforms if '__' not in platform]

    # List all directories in directory
    return platforms


# --------------------------------------------------------------------------------------------------


def login_or_compute(platform) -> str:

    # Open the properties file
    properties_file = os.path.join(platform_path(), 'properties.yaml')

    # If properties file does not exist return login to be safe
    if not os.path.exists(properties_file):
        return 'login'

    with open(properties_file, 'r') as properties_file_open:
        properties = yaml.safe_load(properties_file_open)

    # Query the hostname by issuing shell command hostname
    hostname = os.popen('hostname').read().strip()

    if properties['hostname']['login'] in hostname:
        return 'login'
    elif properties['hostname']['compute'] in hostname:
        return 'compute'

    # Fallback to returning login to be safe
    return 'login'


# --------------------------------------------------------------------------------------------------
