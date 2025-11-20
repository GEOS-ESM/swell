# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
from typing import Optional
import yaml

from swell.tasks.task_attributes import TaskAttributes
from swell.utilities.logger import get_logger
from swell.deployment.prepare_config_and_suite.prepare_config_and_suite import \
    PrepareExperimentConfigAndSuite
from swell.utilities.slurm import prepare_slurm_defaults_and_overrides
from swell.utilities.dictionary import add_comments_to_dictionary
from swell.deployment.create_experiment import template_modules_file, create_modules_csh
from swell.utilities.jinja2 import template_string_jinja2
from swell.utilities.shell_commands import create_executable_file

# --------------------------------------------------------------------------------------------------

script_template = '''
#!{{shell}}
{%- for key, value in task_slurm_dict.items() %}
#SBATCH --{{key}} = {{value}}
{%- endfor %}

# -------------------

source {{modules_file}}

# -------------------

{{script}}

# -------------------
'''


# --------------------------------------------------------------------------------------------------

def task_config_wrapper(task_name: str,
                        platform: str,
                        datetime: Optional[str],
                        model: Optional[str],
                        input_method: str,
                        override: str,
                        slurm: str,
                        cwd: bool) -> None:

    # Create logger
    logger = get_logger('SwellTaskConfig')

    logger.info(f'Generating config for task {task_name}')

    # Get the task attributes for the class
    task_attr_class = getattr(TaskAttributes, task_name)
    task = task_attr_class(model=model, platform=platform)

    # Check that model is specified for the task
    if task.is_model and model is None:
        logger.abort('Task requires model (e.g. geos_marine, geos_atmsophere)'
                     ' but none was specified at the command line.')

    # Check that datetime is specified for the task
    if task.is_cycling and datetime is None:
        logger.abort('Task requires datetime (e.g. 20231010T000000Z)'
                     ' but none was specified at the command line.')

    # Construct overrides
    if override is None:
        override = {}

    if model is not None:
        override['model_components'] = [model]
    else:
        override['model_components'] = []

    # Build in current working directory
    if cwd:
        override['experiment_root'] = os.getcwd()

    # Construct task ID
    task_id = f'swell-{task_name}'
    if model is not None:
        task_id = task_id + f'-{model}'

    if datetime is not None:
        task_id = task_id + f'-{datetime}'

    if 'experiment_id' not in override:
        override['experiment_id'] = task_id

    # Don't put results in cycle dir
    if 'use_cycle_dir' not in override:
        override['use_cycle_dir'] = False

    # Build the suite for task minimums
    prepare_config_and_suite = PrepareExperimentConfigAndSuite(logger=logger,
                                                               suite='task_minimum',
                                                               suite_config='task_minimum',
                                                               platform=platform,
                                                               config_client=input_method,
                                                               override=override)

    # Set the tasks appropriately
    model_independent_tasks = []
    model_dependent_tasks = {}

    if model is None:
        model_independent_tasks.append(task)
    else:
        model_dependent_tasks[model] = [task]

    prepare_config_and_suite.model_independent_tasks = model_independent_tasks
    prepare_config_and_suite.model_dependent_tasks = model_dependent_tasks

    # Configure and ask all questions
    experiment_dict, comment_dict = prepare_config_and_suite.configure_and_ask_task_questions()

    # Expand all environment vars in the dictionary
    experiment_dict_string = yaml.dump(experiment_dict, default_flow_style=False, sort_keys=False)
    experiment_dict_string = os.path.expandvars(experiment_dict_string)
    experiment_dict = yaml.safe_load(experiment_dict_string)

    # Add comments to dictionary
    experiment_dict_string = yaml.dump(experiment_dict, default_flow_style=False, sort_keys=False)

    experiment_dict_string_comments = add_comments_to_dictionary(logger, experiment_dict_string,
                                                                 comment_dict)

    # Construct the slurm defaults
    slurm_external_dict = prepare_slurm_defaults_and_overrides(logger, platform, slurm)

    # Construct the slurm dict for the task
    if task.slurm is not None:
        task_slurm_dict = task.generate_task_slurm_dict(slurm_external_dict, platform)
    else:
        task_slurm_dict = {}

    # Determine the path for task results
    experiment_root = experiment_dict['experiment_root']
    experiment_id = experiment_dict['experiment_id']

    task_path = os.path.join(experiment_root, experiment_id)

    # If use_cycle_dir, construct the experiment directory the same way as a suite
    if experiment_dict['use_cycle_dir']:
        task_path = os.path.join(task_path, f'{experiment_id}-suite')

    # Create the task directory
    os.makedirs(task_path, exist_ok=True)

    # Write the task config
    config_file = os.path.join(task_path, 'task_config.yaml')
    with open(config_file, 'w') as f:
        f.write(experiment_dict_string_comments)

    logger.info(f'Writing task config under {config_file}')

    # Build the modules file depending on the suite
    shell = os.environ.get('SHELL')
    if shell is not None and 'bash' in shell:
        template_modules_file(logger, experiment_dict, task_path)
        modules_file = os.path.join(task_path, 'modules')
        shell_type = 'bash'
    elif shell is not None and 'csh' in shell:
        create_modules_csh(logger, task_path)
        modules_file = os.path.join(task_path, 'modules-csh')
        shell_type = 'csh'
    else:
        # Default to bash
        template_modules_file(logger, experiment_dict, task_path)
        create_modules_csh(logger, task_path)
        logger.info('Shell type not detected, make sure you have the proper modules'
                    ' loaded before running experiment')
        modules_file = os.path.join(task_path, 'modules')
        shell_type = 'bash'

    file_ext = shell_type
    if len(task_slurm_dict) > 0:
        file_ext = 'slurm'

    # Build the swell task script
    script = f'swell task {task_name} {config_file}'
    if model is not None:
        script += f' -m {model}'

    if datetime is not None:
        script += f' -d {datetime}'

    # Build the template dict for the shell script file
    script_dict = {}
    script_dict['shell'] = shell
    script_dict['task_slurm_dict'] = task_slurm_dict
    script_dict['modules_file'] = modules_file
    script_dict['script'] = script

    # Template the shell script
    script_content = template_string_jinja2(logger,
                                            templated_string=script_template,
                                            dictionary_of_templates=script_dict)

    # Create the shell script file
    script_file = os.path.join(task_path, f'{task_id}.{file_ext}')
    create_executable_file(logger, script_file, script_content)

    logger.info('Task config successfully generated.')
    logger.info('To run the task by itself, run: ')
    print(f'\n  {script}\n')
    logger.info('Or, to use auto-generated script, run: ')
    if len(task_slurm_dict) > 0:
        print(f'\n  sbatch {script_file}\n')
    else:
        print(f'\n  {script_file}\n')

# --------------------------------------------------------------------------------------------------
