#!/usr/bin/env python

# (C) Copyright 2022 United States Government as represented by the Administrator of the
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
@click.option('-s', '--suite', 'suite', default='hofx', help='If using defaults for input_method ' +
              'this option is used to determine which suite to obtain the defaults for.')
@click.option('-p', '--platform', 'platform', default='nccs_discover', help='If using defaults ' +
              'for input_method this option is used to determine which platform to use for ' +
              'platform specific defaults.')
@click.option('-o', '--override', 'override', default=None, help='After generating the config ' +
              'file parameters inside can be overridden using value from the override config file.')
def main(input_method, suite, platform, override):

    # Welcome message
    # ---------------
    write_welcome_message('Prepare Config')

    # Create suites object
    # --------------------
    config_file = prepare_config(input_method, suite, platform, override)


# --------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    main()


# --------------------------------------------------------------------------------------------------
