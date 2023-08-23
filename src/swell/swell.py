# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

import click

from swell.deployment.prep_config import prepare_config
from swell.utilities.welcome_message import write_welcome_message

# --------------------------------------------------------------------------------------------------

# Driver
# ------
@click.group()
def swell_driver():
    pass

# Create experiment
# -----------------
@swell_driver.command()
@click.option('-m', '--input_method', 'input_method', default='defaults', help='Method by which ' +
              'to create the YAML configuration file. Valid choices: \'defaults\', \'cli\'.')
@click.option('-p', '--platform', 'platform', default='nccs_discover', help='If using defaults ' +
              'for input_method this option is used to determine which platform to use for ' +
              'platform specific defaults.')
@click.option('-o', '--override', 'override', default=None, help='After generating the config ' +
              'file parameters inside can be overridden using value from the override config file.')
@click.option('-t', '--test', 'test', default=None, help='Override defaults with a preprepared ' +
              'test config file.')
def create_experiment(config):

    # Prepare the experiment config file
    prepare_config(input_method, suite, platform, override, test)


    click.echo("Running")

# Launch experiment
# ------------------
@swell_driver.command()
@click.option('-p', '--suite_path', 'suite_path', default=None,
              help='Directory containing the suite file needed by the workflow manager')
@click.option('-b', '--no-detach', 'no_detach', is_flag=True, default=False,
              help='Tells workflow manager to block until complete')
@click.option('-l', '--log_path', 'log_path', default=None,
              help='Directory to receive workflow manager logging output')
def launch_experiment():
    click.echo("Launching...")

# Tasks
# -----
@swell_driver.command()
@click.argument('taskname')
def task(taskname):
    click.echo("Task ")
    print(taskname)

# Utilities
# ---------
@swell_driver.command()
@click.argument('utility')
def utility(utility):
    click.echo("Utility ")
    print(utility)

# Main
# ----
def main():
    write_welcome_message()

    swell_driver()
