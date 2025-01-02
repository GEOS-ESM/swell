# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import click
from typing import Union, Optional, Literal

from swell.deployment.platforms.platforms import get_platforms
from swell.deployment.create_experiment import clone_config, create_experiment_directory
from swell.deployment.launch_experiment import launch_experiment
from swell.tasks.base.task_base import task_wrapper, get_tasks
from swell.test.test_driver import test_wrapper, valid_tests
from swell.test.suite_tests.suite_tests import run_suite, TestSuite
from swell.utilities.suite_utils import get_suites
from swell.utilities.welcome_message import write_welcome_message
from swell.utilities.scripts.utility_driver import get_utilities, utility_wrapper


# --------------------------------------------------------------------------------------------------


@click.group()
def swell_driver() -> None:
    """
    Welcome to swell!

    This is the top level driver for swell. It serves as a container for various commands
    related to experiment creation, launching, tasks, and utilities.

    The normal process for creating and running an experiment is to issue:

      swell create <suite_name>

    followed by

      swell launch <suite_path>

    """
    pass


# --------------------------------------------------------------------------------------------------

# Help strings for optional arguments

input_method_help = 'Method by which to create the YAML configuration file. If choosing ' + \
                    'defaults the setting for the default suite test will be used. If using ' + \
                    'CLI you will be led through the questions to configure the experiment.'

platform_help = 'If using defaults for input_method, this option is used to determine which ' + \
                'platform to use for platform specific defaults. Options are ' + \
                str(get_platforms())

override_help = 'After generating the config file, parameters inside can be overridden ' + \
                'using values from the override config file.'

advanced_help = 'Show configuration questions which are otherwise not shown to the user.'

no_detach_help = 'Tells the workflow manager not to detach. That is to say run the entire ' + \
                 'run the entire workflow in the foreground and pass back a return code.'

log_path_help = 'Directory to receive workflow manager logging output (instead of ' + \
                '$HOME/cylc-run/<suite_name>)'

datetime_help = 'Datetime to use for task execution. Format is yyyy-mm-ddThh:mm:ss. Note that ' + \
                'non-numeric characters will be stripped from the string. Minutes and seconds ' + \
                'are optional.'

model_help = 'Data assimilation system. I.e. the model being initialized by data assimilation.'

ensemble_help = 'When handling ensemble workflows using a parallel strategy, ' + \
                'specify which packet of ensemble members to consider.'

slurm_help = """
Customize SLURM directives, globally (e.g., account name), for specific tasks,
or for task-model combinations.
"""


# --------------------------------------------------------------------------------------------------


@swell_driver.command()
@click.argument('suite', type=click.Choice(get_suites()))
@click.option('-m', '--input_method', 'input_method', default='defaults',
              type=click.Choice(['defaults', 'cli']), help=input_method_help)
@click.option('-p', '--platform', 'platform', default='nccs_discover_sles15',
              type=click.Choice(get_platforms()), help=platform_help)
@click.option('-o', '--override', 'override', default=None, help=override_help)
@click.option('-a', '--advanced', 'advanced', default=False, help=advanced_help)
@click.option('-s', '--slurm', 'slurm', default=None, help=slurm_help)
def create(
    suite: str,
    input_method: str,
    platform: str,
    override: Union[dict, str, None],
    advanced: bool,
    slurm: str
) -> None:
    """
    Create a new experiment

    This command creates an experiment directory based on the provided suite name and options.

    Arguments: \n
        suite (str): Name of the suite you wish to run. \n

    """
    # Create the experiment directory
    create_experiment_directory(suite, input_method, platform, override, advanced, slurm)


# --------------------------------------------------------------------------------------------------


@swell_driver.command()
@click.argument('configuration')
@click.argument('experiment_id')
@click.option('-m', '--input_method', 'input_method', default='defaults',
              type=click.Choice(['defaults', 'cli']), help=input_method_help)
@click.option('-p', '--platform', 'platform', default=None, help=platform_help)
@click.option('-a', '--advanced', 'advanced', default=False, help=advanced_help)
def clone(
    configuration: str,
    experiment_id: str,
    input_method: str,
    platform: str,
    advanced: bool
) -> None:
    """
    Clone an existing experiment

    This command creates an experiment directory based on the provided experiment configuration.

    Arguments: \n
        configuration (str): Path to a YAML containing the experiment configuration you wish to
        clone from. \n

    """
    # Create experiment configuration by cloning from existing experiment
    experiment_dict_str = clone_config(configuration, experiment_id, input_method, platform,
                                       advanced)

    # Create the experiment directory
    create_experiment_directory(experiment_dict_str)


# --------------------------------------------------------------------------------------------------


@swell_driver.command()
@click.argument('suite_path')
@click.option('-b', '--no-detach', 'no_detach', is_flag=True, default=False, help=no_detach_help)
@click.option('-l', '--log_path', 'log_path', default=None, help=log_path_help)
def launch(
    suite_path: str,
    no_detach: bool,
    log_path: str
) -> None:
    """
    Launch an experiment with the cylc workflow manager

    This command launches an experiment using the provided suite path and options.

    Arguments: \n
        suite_path (str): Path to where the flow.cylc and associated suite files are located. \n

    """
    launch_experiment(suite_path, no_detach, log_path)


# --------------------------------------------------------------------------------------------------


@swell_driver.command()
@click.argument('task', type=click.Choice(get_tasks()))
@click.argument('config')
@click.option('-d', '--datetime', 'datetime', default=None, help=datetime_help)
@click.option('-m', '--model', 'model', default=None, help=model_help)
@click.option('-p', '--ensemblePacket', 'ensemblePacket', default=None, help=ensemble_help)
def task(
    task: str,
    config: str,
    datetime: Optional[str],
    model: Optional[str],
    ensemblePacket: Optional[str]
) -> None:
    """
    Run a workflow task

    This command executes a task using the provided task name, configuration file and options.

    Arguments:\n
        task (str): Name of the task to execute.\n
        config (str): Path to the configuration file for the task.\n

    """
    task_wrapper(task, config, datetime, model, ensemblePacket)


# --------------------------------------------------------------------------------------------------


@swell_driver.command()
@click.argument('utility', type=click.Choice(get_utilities()))
def utility(utility: str) -> None:
    """
    Run a utility script

    This command performs a utility operation specified by the utility argument.

    Arguments:\n
        utility (str): Name of the utility operation to perform.\n

    """
    utility_wrapper(utility)


# --------------------------------------------------------------------------------------------------


@swell_driver.command()
@click.argument('test', type=click.Choice(valid_tests))
def test(test: str) -> None:
    """
    Run one of the test suites

    This command performs the test specified by the test argument.

    Arguments:\n
        test (str): Name of the test to execute.

    """
    test_wrapper(test)


# --------------------------------------------------------------------------------------------------


@swell_driver.command()
@click.option('-p', '--platform', 'platform', type=click.Choice(get_platforms()),
              default="nccs_discover_sles15", help=platform_help)
@click.argument('suite', type=click.Choice(("hofx", "3dvar", "ufo_testing")))
def t1test(
    suite: Literal["hofx", "3dvar", "ufo_testing"],
    platform: Optional[str] = "nccs_discover_sles15"
) -> None:
    """
    Run a particular swell suite from the tier 1 tests.

    Arguments:
        suite (str): Name of the suite to run (e.g., hofx, 3dvar, ufo_testing)
    """
    run_suite(suite, platform, TestSuite.TIER1)


# --------------------------------------------------------------------------------------------------


@swell_driver.command()
@click.option('-p', '--platform', 'platform', type=click.Choice(get_platforms()),
              default="nccs_discover_sles15", help=platform_help)
@click.argument('suite', type=click.Choice(("hofx", "3dvar", "ufo_testing",
                                            "convert_ncdiags", "3dfgat_atmos", "build_jedi")))
def t2test(
    suite: Literal["hofx", "3dvar", "ufo_testing",
                   "convert_ncdiags", "3dfgat_atmos", "build_jedi"],
        platform: Optional[str] = "nccs_discover_sles15"
) -> None:
    """
    Run a particular swell suite from the tier 2 tests.

    Arguments:
        suite (str): Name of the suite to run (e.g., hofx, 3dvar, ufo_testing)
    """
    run_suite(suite, platform, TestSuite.TIER2)


# --------------------------------------------------------------------------------------------------


def main() -> None:
    """
    Main Function

    This function is the entry point for swell. It writes a welcome message and
    sets up the driver group.
    """
    write_welcome_message()
    swell_driver()


# --------------------------------------------------------------------------------------------------
