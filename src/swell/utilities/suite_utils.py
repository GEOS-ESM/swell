# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import glob
import os

from swell.swell_path import get_swell_path
from swell.suites.suite_questions import SuiteQuestions as suite_questions


# --------------------------------------------------------------------------------------------------


def get_suites() -> list:

    # Path to platforms
    suites_directory = os.path.join(get_swell_path(), 'suites')

    # List of base suites
    suites = sorted([sdir for sdir in os.listdir(suites_directory)
              if (os.path.isdir(os.path.join(suites_directory, sdir))
              and os.path.exists(os.path.join(suites_directory, sdir, 'flow.cylc')))])

    # List of suites and associated sub-suites
    suite_config_list = []

    for suite in suites:
        suite_sub_list = []
        [suite_sub_list.append(suite_config[1:] if suite_config[0]=='_' else suite_config) for suite_config in suite_questions.get_all() if suite_questions[suite_config].value.list_name == suite and '_base' not in suite_config]
        suite_config_list.extend(sorted(suite_sub_list))

    # List all directories in platform_directory
    return suite_config_list


# --------------------------------------------------------------------------------------------------


def get_suite_tests() -> list:

    # Path to platforms
    suite_tests_directory = os.path.join(get_swell_path(), 'test', 'suite_tests', '*.yaml')

    # List of tasks
    suite_test_files = sorted(glob.glob(suite_tests_directory))

    # Get just the task name
    suite_tests = []
    for suite_test_file in suite_test_files:
        suite_tests.append(os.path.basename(suite_test_file)[0:-5])

    # Sort list alphabetically
    suite_tests = sorted(suite_tests)

    # Return list of valid task choices
    return suite_tests


# --------------------------------------------------------------------------------------------------
