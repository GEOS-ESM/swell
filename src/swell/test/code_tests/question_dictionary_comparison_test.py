# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import unittest

from swell.utilities.scripts.compare_questions import compare_used_and_set_questions


# --------------------------------------------------------------------------------------------------


class QuestionDictionaryTest(unittest.TestCase):

    def test_dictionary_comparison(self):

        used_not_set, set_not_used = compare_used_and_set_questions()

        # Throw error if there are any unassigned variables used by the code
        if len(used_not_set) > 0:
            error_msg = ("Questions which are required by the code are missing from the question "
                         "configurations:\n\n")

            for suite in used_not_set.keys():
                for task_or_suite in used_not_set[suite]:
                    questions_str = ""
                    for q in used_not_set[suite][task_or_suite]:
                        questions_str += q + '\n'
                    error_msg += (f"In suite {suite}, the {task_or_suite} question configuration "
                                  f"is missing the required question(s):\n{questions_str}\n")

        assert len(used_not_set) == 0, error_msg

        # TODO: Implement a check for set-but-not-used questions
        # This will require a fix/adjustment for some suites

# --------------------------------------------------------------------------------------------------
