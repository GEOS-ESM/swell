# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os

from swell.swell_path import get_swell_path


# --------------------------------------------------------------------------------------------------


def get_model_components() -> list:

    # Path to model interfaces
    interface_directory = os.path.join(get_swell_path(), 'configuration', 'jedi', 'interfaces')

    # Get models
    return os.listdir(interface_directory)

# --------------------------------------------------------------------------------------------------
