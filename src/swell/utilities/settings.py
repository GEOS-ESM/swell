# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import yaml

# --------------------------------------------------------------------------------------------------

def read_settings() -> dict:
    '''
    Reads user settings from yaml file under ~/.swell/swell-settings.yaml

    Args:
        None

    Returns:
        Dictionary of settings specified in file.
    '''
    settings_file = os.path.expanduser(os.path.join('~', '.swell', 'swell-settings.yaml'))

    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            settings_dict = yaml.safe_load(f)
        
    else:
        settings_dict = {}

    return settings_dict

# --------------------------------------------------------------------------------------------------