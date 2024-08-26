# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import unittest

from swell.test.code_tests.question_dictionary_comparison_test import QuestionDictionaryTest
from swell.test.code_tests.unused_variables_test import UnusedVariablesTest
from swell.test.code_tests.slurm_test import SLURMConfigTest
from swell.utilities.logger import Logger


# --------------------------------------------------------------------------------------------------

def code_tests():

    # Create a logger
    logger = Logger('TestSuite')
    logger.test('Running Swell Test Suite')

    # Check for environment variable
    log_env = os.environ.get('LOG_INFO')

    # If found set element to environment variable
    if log_env is None:
        # Turn off the regular info testing (default)
        os.environ["LOG_INFO"] = "0"  # Set this to 1 when errors are being debugged
    else:
        os.environ["LOG_INFO"] = log_env

    # Create a test suite
    test_suite = unittest.TestSuite()

    # Load unused variable test
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(UnusedVariablesTest))

    # Load tests from UnusedVariablesTest
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(QuestionDictionaryTest))

    # Load SLURM tests
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(SLURMConfigTest))

    # Create a test runner
    test_runner = unittest.TextTestRunner()

    # Run the tests
    test_result = test_runner.run(test_suite)

    # Ensure everything was successful
    logger.assert_abort(test_result.wasSuccessful(), "Swell code tests failed")

# --------------------------------------------------------------------------------------------------
