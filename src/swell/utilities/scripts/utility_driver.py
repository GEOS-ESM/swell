# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import glob
import os
import importlib

from swell.swell_path import get_swell_path
from swell.utilities.case_switching import snake_case_to_camel_case
from swell.test.code_tests.code_tests import code_tests


# --------------------------------------------------------------------------------------------------

def get_utilities():

    # Path to util scripts
    util_scripts_dir = os.path.join(get_swell_path(), 'utilities', 'scripts', '*.py')

    # List of tasks
    util_script_files = sorted(glob.glob(util_scripts_dir))

    # Get just the task name
    util_scripts = []
    for util_script_file in util_script_files:
        base_name = os.path.basename(util_script_file)
        if '__' not in base_name:
            util_scripts.append(snake_case_to_camel_case(base_name[0:-3]))

    # Return list of valid task choices
    return util_scripts

# --------------------------------------------------------------------------------------------------

def utility_wrapper(utility):

    # Test script
    test_script_file = 'swell.utility.scripts.'+utility+'.'+utility

    # Import the correct method
    utility_method = getattr(importlib.import_module(test_script_file), utility)

    # Run the test
    utility_method()
