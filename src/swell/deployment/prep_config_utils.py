# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from swell.swell_path import get_swell_path


# --------------------------------------------------------------------------------------------------


def get_platforms():

    # Path to platforms
    platform_directory = os.path.join(get_swell_path(), 'deployment', 'platforms')

    platforms = [dir for dir in os.listdir(platform_directory)
                 if os.path.isdir(os.path.join(platform_directory, dir))]

    # If anything in platforms contains '__' remove it from platforms list
    platforms = [platform for platform in platforms if '__' not in platform]

    # List all directories in platform_directory
    return platforms


# --------------------------------------------------------------------------------------------------
