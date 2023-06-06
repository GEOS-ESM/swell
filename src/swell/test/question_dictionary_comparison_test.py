# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import unittest
import yaml

from swell.swell_path import get_swell_path
from swell.utilities.bin.generate_task_questions_dict import main as generate_task_questions_dict


# --------------------------------------------------------------------------------------------------

class QuestionDictionaryTest(unittest.TestCase):

    def test_dictionary_comparison(self):

        # Run dictionary generation
        return_code = generate_task_questions_dict()

        # Assert that dictionaries are equal
        assert return_code == 0

# --------------------------------------------------------------------------------------------------
