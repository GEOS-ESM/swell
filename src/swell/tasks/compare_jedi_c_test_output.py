# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import re
import subprocess
import yaml
import glob
import re

from swell.tasks.base.task_base import taskBase
from swell.utilities.suite_utils import get_model_components

# --------------------------------------------------------------------------------------------------


class CompareJediCTestOutput(taskBase):

    def execute(self) -> None:

        # Create dictionaries to track the ctest results
        comparison_dict_0 = {}
        comparison_dict_1 = {}

        # Find the results files
        ctest_output_files = sorted(glob.glob(os.path.join(
            self.experiment_path(), 'comparison_tests', 'jedi_ctest_results*txt')))

        # Get the results from each file
        for i, file in enumerate(ctest_output_files):
            with open(file, 'r') as f:
                lines = f.readlines()

            comparison_dict[str(i)] = {}

            for line in lines:
                if re.match('[0-9]*/[0-9]* Test'):
                    test = int(line.split('/')[0].strip())
                    if 'Passed' in line:
                        status = True
                    else:
                        status = False

                    comparison_dict[str(i)][str(test)] = status

        # Make sure that the number of tests match
        if len(comparison_dict_0) != len(comparison_dict_1):
            self.logger.info('The two JEDI versions specified do not'
                             ' share the same number of ctests')

        else:

            # Match the tests
            for test in comparison_dict_0.keys():
                if comparison_dict_0[test] and comparison_dict_1[test]:
                    test_0 = 'Passed' if comparison_dict_0[test] else 'Failed'
                    test_1 = 'Passed' if comparison_dict_1[test] else 'Failed'

                    self.logger.info(f'Mismatch in test #{test}: Build 0'
                                     f' {test_0}, Build 1 {test_1}')


# --------------------------------------------------------------------------------------------------
