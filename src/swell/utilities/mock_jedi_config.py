# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import shutil
import tempfile

from swell.tasks.base.task_base import task_wrapper
from swell.deployment.create_experiment import create_experiment_directory

# --------------------------------------------------------------------------------------------------

def mock_jedi_config(suite: str,
                     model: str,
                     datetime: str,
                     executable_type: str,
                     copy_to_wd: bool = False) -> str:
    
    tempdir = tempfile.mkdtemp()

    override_dict = {'models': {}}
    override_dict['experiment_root'] = tempdir
    override_dict['generate_yaml_and_exit'] = True
    override_dict['models'][model] = {'check_for_obs': False,
                                      'mock_experiment_directory': True}
    
    create_experiment_directory(suite, method='defaults', platform='nccs_discover_sles15',
                                override=override_dict, advanced=False, slurm=None, skip_r2d2=True)

    experiment_yaml = os.path.join(tempdir, f'swell-{suite}',
                                   f'swell-{suite}-suite', 'experiment.yaml')

    task_wrapper('RenderJediObservations', experiment_yaml, datetime,
                 model, ensemblePacket=None)

    task_wrapper(f'RunJedi{executable_type.capitalize()}Executable', experiment_yaml, datetime,
                 model, ensemblePacket=None)

    cycle_dir = os.path.join(tempdir, f'swell-{suite}', 'run', datetime, model)

    filename = f'jedi_{executable_type}_config.yaml'
    config_file = os.path.join(cycle_dir, filename)

    if copy_to_wd:
        new_path = os.path.join(os.getcwd(), f'jedi_{suite}_config.yaml')
        shutil.copy(config_file, new_path)
        config_file = new_path

    return config_file

# --------------------------------------------------------------------------------------------------
