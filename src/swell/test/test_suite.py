# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import unittest

from swell.test.question_dictionary_comparison_test import QuestionDictionaryTest
from swell.test.unused_variables_test import UnusedVariablesTest


# --------------------------------------------------------------------------------------------------

def main():

    # Create a test suite
    test_suite = unittest.TestSuite()

    # Load unused variable test
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(UnusedVariablesTest))

    # Load tests from UnusedVariablesTest
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(QuestionDictionaryTest))

    # Create a test runner
    test_runner = unittest.TextTestRunner()

    # Run the tests
    test_runner.run(test_suite)

# --------------------------------------------------------------------------------------------------
