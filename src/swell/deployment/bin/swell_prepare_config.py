#!/usr/bin/env python

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


@click.command()
@click.option('-m', '--input_method', 'input_method', default='defaults', help='Method by which ' +
              'to create the YAML configuration file. Valid choices: \'defaults\', \'cli\'.')
@click.option('-p', '--platform', 'platform', default='nccs_discover', help='If using defaults ' +
              'for input_method this option is used to determine which platform to use for ' +
              'platform specific defaults.')
@click.option('-o', '--override', 'override', default=None, help='After generating the config ' +
              'file parameters inside can be overridden using value from the override config file.')
@click.option('-t', '--test', 'test', default=None, help='Override defaults with a preprepared ' +
              'test config file.')
@click.option('-a', '--advanced', 'advanced', default=False, help='Show configuration questions ' +
              'which are otherwise not shown to the user.')
@click.argument('suite')
def main(input_method, suite, platform, override, test, advanced):
    """
        SUITE argument determines which set of tasks are going to be run.
    """

    # Welcome message
    # ---------------
    write_welcome_message('Prepare Config')

    # Create suites object
    # --------------------
    prepare_config(input_method, suite, platform, override, test, advanced)


# --------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    main()


# --------------------------------------------------------------------------------------------------
