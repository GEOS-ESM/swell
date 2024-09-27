# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import unittest

from swell.utilities.logger import Logger
from swell.test.code_tests.slurm_test import SLURMConfigTest
from swell.test.code_tests.test_pinned_versions import PinnedVersionsTest
from swell.test.code_tests.unused_variables_test import UnusedVariablesTest
from swell.test.code_tests.question_dictionary_comparison_test import QuestionDictionaryTest
from swell.test.code_tests.test_generate_observing_system import GenerateObservingSystemTest


# --------------------------------------------------------------------------------------------------

def code_tests() -> None:

    # Create a logger
    logger = Logger('TestSuite')
    logger.test('Running Swell Test Suite')

    # Default log_info testing to false
    os.environ.setdefault("LOG_INFO", "0")
    # Set to 1 when errors are being debugged

    # Create a test suite
    test_suite = unittest.TestSuite()

    # Load unused variable test
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(UnusedVariablesTest))

    # Load tests from UnusedVariablesTest
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(QuestionDictionaryTest))

    # Load SLURM tests
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(SLURMConfigTest))

    # Load Observing System Generation tests
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(GenerateObservingSystemTest))

    # Load Pinned Versions Test
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(PinnedVersionsTest))

    # Create a test runner
    test_runner = unittest.TextTestRunner()

    # Run the tests
    test_result = test_runner.run(test_suite)

    # Ensure everything was successful
    logger.assert_abort(test_result.wasSuccessful(), "Swell code tests failed")

# --------------------------------------------------------------------------------------------------
