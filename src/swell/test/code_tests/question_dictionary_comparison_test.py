# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import unittest

# from swell.utilities.scripts.task_question_dicts import main as tq_dicts
from swell.utilities.scripts.task_question_dicts_defaults import main as tq_dicts_defaults


# --------------------------------------------------------------------------------------------------


class QuestionDictionaryTest(unittest.TestCase):

    def test_dictionary_comparison(self):

        # Run main task question dictionary generation
        # tq_dicts_rc = tq_dicts()
        # assert tq_dicts_rc == 0

        # Run generation for defaults
        tq_dicts_defaults_rc = tq_dicts_defaults()
        assert tq_dicts_defaults_rc == 0


# --------------------------------------------------------------------------------------------------
