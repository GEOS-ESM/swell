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
from swell.deployment.create_experiment import create_experiment_directory
from swell.tasks.base.task_base import task_wrapper

# --------------------------------------------------------------------------------------------------

def test_jedi_config(suite: str,
                     model: str,
                     datetime: str,
                     executable_type: str) -> None:

    tempdir = tempfile.mkdtemp()

    override_dict = {'models': {}}
    override_dict['experiment_root'] = tempdir
    override_dict['models'][model] = {'check_for_obs': False,
                                      'generate_yaml_and_exit': True}
    
    create_experiment_directory(suite, 'defaults', 'nccs_discover_sles15',
                                override_dict, 'defaults', None)
    
    experiment_yaml = os.path.join(tempdir, f'swell-{suite}',
                                   f'swell-{suite}-suite', 'experiment.yaml')

    task_wrapper('RenderJediObservations', experiment_yaml, datetime,
                 model, ensemblePacket=None)

    task_wrapper(f'RunJedi{executable_type.upper()}Executable', experiment_yaml, datetime,
                 model, ensemblePacket=None)
    
    cycle_dir = os.path.join(tempdir, f'swell-{suite}', 'run', datetime, model)

    config_file = os.path.join(cycle_dir, f'jedi_{executable_type}_config.yaml')

    yaml = YAML(typ='safe')

    with open(config_file, 'r') as f:
        config_dict = yaml.load(f)

    comparison_config = os.path.join(get_swell_path(), 'test', f'jedi_config_{suite}.yaml')

    with open(comparison_config, 'r') as f:
        comparison_dict = yaml.load(f)

    assert config_dict == comparison_dict

# --------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    test_jedi_config('3dvar_marine')

# --------------------------------------------------------------------------------------------------