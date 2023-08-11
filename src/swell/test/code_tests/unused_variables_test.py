# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import unittest
import subprocess
import os

from swell.swell_path import get_swell_path


# --------------------------------------------------------------------------------------------------


def run_flake8(file_path):
    flake8_cmd = ['flake8', '--select', 'F401,F841', file_path]
    result = subprocess.run(flake8_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            universal_newlines=True)
    return result.stdout.strip()


# --------------------------------------------------------------------------------------------------


class UnusedVariablesTest(unittest.TestCase):

    def test_unused_variables(self):

        for root, _, files in os.walk(get_swell_path()):
            for filename in files:
                if filename.endswith('.py'):  # Only process Python files
                    file_path = os.path.join(root, filename)
                    flake8_output = run_flake8(file_path)

                    self.assertEqual(flake8_output, '', f"Unused variables found in {file_path}")


# --------------------------------------------------------------------------------------------------
