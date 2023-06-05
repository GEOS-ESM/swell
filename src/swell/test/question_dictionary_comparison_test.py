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

        # First test the
        destination_yaml = os.path.join(get_swell_path(), 'tasks', 'task_questions.yaml')

        # Read input file into dictionary
        with open(destination_yaml, 'r') as ymlfile:
            question_dict = yaml.safe_load(ymlfile)
        question_dict_in = question_dict.copy()

        # Run dictionary generation
        generate_task_questions_dict()

        # Read new dictionary
        with open(destination_yaml, 'r') as ymlfile:
            question_dict = yaml.safe_load(ymlfile)

        # Assert that dictionaries are equal
        self.assertDictEqual(question_dict_in, question_dict)


# --------------------------------------------------------------------------------------------------
