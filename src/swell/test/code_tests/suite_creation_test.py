# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import tempfile
import os
from ruamel.yaml import YAML
import unittest

from swell.suites.all_suites import get_suites
from swell.deployment.create_experiment import create_experiment_directory

# --------------------------------------------------------------------------------------------------

class SuiteCreationTest(unittest.TestCase):

    def run_suite_creation_test(self) -> None:

        suites = get_suites()

        for suite in suites:
            self.suite_creation_test(suite)

    def suite_creation_test(self, suite: str) -> None:

        tempdir = tempfile.mkdtemp()

        override_dict = {}

        override_dict['experiment_root'] = tempdir
        override_dict['skip_r2d2'] = True

        create_experiment_directory(suite, 'defaults', 'nccs_discover_sles15',
                                    override_dict, False, None)
        
        experiment_yaml = os.path.join(tempdir, f'swell-{suite}', f'swell-{suite}-suite', 'experiment.yaml')

        yaml = YAML(typ='safe')

        with open(experiment_yaml, 'r') as f:
            experiment_yaml_str = yaml.load(f)

        assert 'defer_to_model' not in experiment_yaml_str
        assert 'defer_to_platform' not in experiment_yaml_str

# --------------------------------------------------------------------------------------------------