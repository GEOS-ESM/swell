# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import unittest
import tempfile

from swell.suites.base.suite_attributes import workflows
from swell.deployment.create_experiment import create_experiment_directory
from swell.utilities.logger import get_logger
from swell.utilities.test_cache import get_test_cache

# --------------------------------------------------------------------------------------------------


class SuiteCreationTest(unittest.TestCase):

    def runTest(self) -> None:

        '''Test generating all suites to make sure they are configured correctly.

        Checks that templates `defer_to_model` and `defer_to_platform` are filled.

        '''

        suites = workflows.all()

        self.logger = get_logger('SuiteCreationTest')

        for suite in suites:
            try:
                self.suite_creation_test(suite)
            except Exception as e:
                raise Exception(f'Error generating {suite} experiment: {e}')

    def suite_creation_test(self, suite: str) -> None:

        cache_location = get_test_cache()
        if cache_location is None:
            cache_location = tempfile.mkdtemp()

        override_dict = {}

        override_dict['experiment_id'] = experiment_id = f'{suite}-creation'
        override_dict['experiment_root'] = cache_location
        override_dict['skip_r2d2'] = True

        create_experiment_directory(suite, 'defaults', 'nccs_discover_sles15',
                                    override_dict, advanced=False, slurm=None, skip_r2d2=True)

        experiment_yaml = os.path.join(cache_location, experiment_id, f'{experiment_id}-suite',
                                       'experiment.yaml')

        with open(experiment_yaml, 'r') as f:
            experiment_yaml_str = f.read()

        if 'defer_to_model' in experiment_yaml_str:
            raise AssertionError(f'Improperly filled template for {suite}, `defer_to_model`'
                                 'present in experiment yaml')

        if 'defer_to_platform' in experiment_yaml_str:
            raise AssertionError(f'Improperly filled template for {suite}, `defer_to_platform`'
                                 'present in experiment yaml')

# --------------------------------------------------------------------------------------------------
