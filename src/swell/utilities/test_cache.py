# (C) Copyright 2023- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from typing import Optional

import os
from ruamel.yaml import YAML

# --------------------------------------------------------------------------------------------------


def get_test_cache() -> Optional[str]:
    test_settings_file = os.path.expanduser('~/.swell/swell-test.yaml')
    if os.path.exists(test_settings_file):
        yaml = YAML(typ='safe')
        with open(test_settings_file, 'r') as f:
            test_settings = yaml.load(f)
        if 'test_cache_location' in test_settings:
            return test_settings['test_cache_location']
    return None

# --------------------------------------------------------------------------------------------------
