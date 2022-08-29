#!/usr/bin/env python

# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from swell.suites.suites import suites

# --------------------------------------------------------------------------------------------------


def main():

    # Create a logger
    # ---------------
    logger = Logger('SwellPrepSuiteConfig')


    # Create suites object
    # --------------------
    suite_config = suites()



# --------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    main()


# --------------------------------------------------------------------------------------------------
