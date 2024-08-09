# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

import importlib

# --------------------------------------------------------------------------------------------------

valid_tests = ['code_tests']

# --------------------------------------------------------------------------------------------------


def test_wrapper(test):

    # Test script
    test_script_file = 'swell.test.'+test+'.'+test

    # Import the correct method
    test_method = getattr(importlib.import_module(test_script_file), test)

    # Run the test
    test_method()


# --------------------------------------------------------------------------------------------------
