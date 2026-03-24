# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import tempfile
from ruamel.yaml import YAML

from swell.swell_path import get_swell_path
from swell.utilities.mock_jedi_config import mock_jedi_config

# --------------------------------------------------------------------------------------------------

def run_test(suite: str,
             model: str,
             datetime: str,
             executable_type: str) -> None:

    config_file = mock_jedi_config(suite, model, datetime, executable_type)

    yaml = YAML(typ='safe')

    with open(config_file, 'r') as f:
        config_dict = yaml.load(f)

    comparison_config = os.path.join(get_swell_path(), 'test', 'jedi_yamls',
                                     f'jedi_config_{suite}.yaml')

    with open(comparison_config, 'r') as f:
        comparison_dict = yaml.load(f)

    assert config_dict == comparison_dict

# --------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    run_test('3dvar_marine', 'geos_marine', '20210701T120000Z', 'variational')

# --------------------------------------------------------------------------------------------------
