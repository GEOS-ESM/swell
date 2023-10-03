# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import click

from swell.deployment.prep_config import prepare_config
from swell.deployment.prep_config_utils import get_platforms
from swell.deployment.create_experiment import create_experiment_directory
from swell.deployment.launch_experiment import launch
from swell.tasks.base.task_base import task_wrapper, get_tasks
from swell.test.test_driver import test_wrapper, valid_tests
from swell.utilities.suite_utils import get_suite_tests, get_suites
from swell.utilities.welcome_message import write_welcome_message


# --------------------------------------------------------------------------------------------------


@click.group()
def swell_driver():
    """
    Swell Driver Group

    This is the main command group for swell. It serves as a container for various commands
    related to experiment creation, launching, tasks, and utilities.
    """
    pass


# --------------------------------------------------------------------------------------------------


@swell_driver.command()
@click.argument('suite', type=click.Choice(get_suites()))
@click.option('-m', '--input_method', 'input_method', default='defaults',
              type=click.Choice(['defaults', 'cli']),
              help='Method by which to create the YAML configuration file. If choosing defaults '
                   'the setting for the default suite test will be used. If using CLI you will be '
                   'led through the questions to configure the experiment.')
@click.option('-p', '--platform', 'platform', type=click.Choice(get_platforms()),
              help='If using defaults for input_method, this option is used '
                   'to determine which platform to use for platform specific defaults.')
@click.option('-o', '--override', 'override', default=None,
              help='After generating the config file, parameters inside can be overridden '
                   'using values from the override config file.')
@click.option('-t', '--test', 'test', default=None, type=click.Choice(get_suite_tests()),
              help='Specify a particular suite test to use for the configuration. This can still '
                   'be overridden.')
def create_experiment(suite, input_method, platform, override, test):
    """
    Create a new experiment configuration and directory

    This command creates an experiment directory based on the provided suite name and options.

    Arguments: \n
        suite (str): Name of the suite you wish to run. \n

    """
    experiment_dict_str = prepare_config(suite, input_method, platform, override, test)
    create_experiment_directory(experiment_dict_str)


# --------------------------------------------------------------------------------------------------


@swell_driver.command()
@click.argument('suite_path')
@click.option('-b', '--no-detach', 'no_detach', is_flag=True, default=False,
              help='Tells the workflow manager not to detach. That is to say run the entire '
                   'run the entire workflow in the foreground and pass back a return code.')
@click.option('-l', '--log_path', 'log_path', default=None,
              help='Directory to receive workflow manager logging output (instead of '
                   '$HOME/cylc-run/<suite_name>)')
def launch_experiment(suite_path, no_detach, log_path):
    """
    Launch an experiment with the cylc workflow manager

    This command launches an experiment using the provided suite path and options.

    Arguments: \n
        suite_path (str): Path to where the flow.cylc and associated suite files are located. \n

    """
    launch(suite_path, no_detach, log_path)


# --------------------------------------------------------------------------------------------------


@swell_driver.command()
@click.argument('task', type=click.Choice(get_tasks()))
@click.argument('config')
@click.option('-d', '--datetime', 'datetime', default=None)
@click.option('-m', '--model', 'model', default=None)
def task(task, config, datetime, model):
    """
    Run a workflow task

    This command executes a task using the provided task name, configuration file and options.

    Arguments:\n
        task (str): Name of the task to execute.\n
        config (str): Path to the configuration file for the task.\n

    """
    task_wrapper(task, config, datetime, model)


# --------------------------------------------------------------------------------------------------


@swell_driver.command()
@click.argument('utility')
def utility(utility):
    """
    Run a utility script

    This command performs a utility operation specified by the utility argument.

    Arguments:\n
        utility (str): Name of the utility operation to perform.\n

    """
    print(utility)


# --------------------------------------------------------------------------------------------------


@swell_driver.command()
@click.argument('test', type=click.Choice(valid_tests))
def test(test):
    """
    Run one of the test suites

    This command performs the test specified by the test argument.

    Arguments:\n
        test (str): Name of the test to execute.

    """
    print(test)
    test_wrapper(test)


# --------------------------------------------------------------------------------------------------


def main():
    """
    Main Function

    This function is the entry point for swell. It writes a welcome message and
    sets up the driver group.
    """
    write_welcome_message()
    swell_driver()


# --------------------------------------------------------------------------------------------------
