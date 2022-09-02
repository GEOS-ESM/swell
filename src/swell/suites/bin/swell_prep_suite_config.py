#!/usr/bin/env python

# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import click
import yaml

from swell.suites.suites import Suites
from swell.utilities.logger import Logger

# --------------------------------------------------------------------------------------------------


@click.command()
@click.argument('method')
@click.argument('top_level_configuration_file')
def main(method, top_level_configuration_file):

    # Create a logger
    # ---------------
    logger = Logger('SwellPrepSuiteConfig')


    # Create suites object
    # --------------------
    suite_config = Suites(method, logger, top_level_configuration_file)


    # Run method to generate the experiment config file
    # -------------------------------------------------
    suite_config.prep_suite_config()


# --------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    main()


# --------------------------------------------------------------------------------------------------
