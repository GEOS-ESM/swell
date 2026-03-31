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
                     work_dir: str | None = None,
                     copy_dir: str | None = None) -> str:

    '''Generate a mock jedi config using the settings for a particular suite. Configs are generated
    in a 'dry-run' mode, without checking for existence of observations. Filepaths are replaced
    with placeholders

    Parameters:
    suite: String of suite within swell
    model: Name of model component for the suite to run (e.g. geos_marine)
    datetime: Cycle that is config is generated for (e.g. 20210701T120000Z)
    executable_type: JEDI executable type (e.g. variational, hofx, fgat)
    copy_dir: Directory to copy rendered file to

    Rendered file is placed under a temporary experiment directory
    '''

    if work_dir is None:
        tempdir = tempfile.mkdtemp()
    else:
        tempdir = work_dir

    override_dict = {'models': {}}
    override_dict['experiment_root'] = tempdir
    override_dict['generate_yaml_and_exit'] = True
    override_dict['mock_experiment'] = True
    override_dict['models'][model] = {'check_for_obs': False}

    create_experiment_directory(suite, method='defaults', platform='nccs_discover_sles15',
                                override=override_dict, advanced=False, slurm=None, skip_r2d2=True)

    experiment_yaml = os.path.join(tempdir, f'swell-{suite}',
                                   f'swell-{suite}-suite', 'experiment.yaml')

    task_wrapper('RenderJediObservations', experiment_yaml, datetime,
                 model, ensemblePacket=None)

    if executable_type == 'localensembleda':
        executable_name = 'LocalEnsembleDa'
    else:
        executable_name = executable_type.capitalize()

    task_wrapper(f'RunJedi{executable_name}Executable', experiment_yaml, datetime,
                 model, ensemblePacket=None)

    cycle_dir = os.path.join(tempdir, f'swell-{suite}', 'run', datetime, model)

    filename = f'jedi_{executable_type}_config.yaml'
    config_file = os.path.join(cycle_dir, filename)

    if copy_dir is not None:
        new_path = os.path.join(copy_dir, f'jedi_{suite}_config.yaml')
        shutil.copy(config_file, new_path)
        config_file = new_path

    return config_file

# --------------------------------------------------------------------------------------------------
