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
@click.argument('method')
def main(method):

    # Welcome message
    # ---------------
    write_welcome_message('Prepare Config')

    # Create suites object
    # --------------------
    config_file = prepare_config(method)


# --------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    main()


# --------------------------------------------------------------------------------------------------
