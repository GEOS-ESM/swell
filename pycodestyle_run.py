#!/usr/bin/env python

# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import unittest
import pycodestyle


# --------------------------------------------------------------------------------------------------


class TestCodeFormat(unittest.TestCase):

    def test_conformance(self):
        """Test that we conform to PEP-8."""
        style = pycodestyle.StyleGuide(config_file='pycodestyle.cfg')
        result = style.check_files(['.'])
        self.assertEqual(result.total_errors, 0, "Found code style errors (and warnings).")


# --------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
